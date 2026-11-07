from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.training.campaign_runtime import (
        IncrementalMirror,
        admit_run,
        phase_deadline,
    )
    from ai_exam_monitoring.training.research_analysis import (
        paired_group_bootstrap,
        recipe_key,
        representative_seed,
        resolve_arm,
    )
    from ai_exam_monitoring.training.research_campaign import (
        ResearchCampaign,
        select_profile,
        tree_equal,
    )


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class ResearchCampaignTests(unittest.TestCase):
    def test_two_seed_screening_then_only_finalists_complete_five_seeds(self):
        for profile, names, top, expected_count in (
            ('full',['C0','S448','SL','SH','S4','B0','BL','B448'],['S4','BL'],25),
            ('core',['C0','S448','SL','SH','S4'],['C0','S4'],16),
        ):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                campaign=ResearchCampaign.__new__(ResearchCampaign)
                campaign.base=Path(tmp)
                campaign.root=Path(tmp)
                campaign.profile=profile
                campaign.state={'started_at':time.time(),'research_runs':[],'runs':{}}
                campaign.budget={'screening_arms':names,'screening_seeds':[1,2],
                    'confirmation_seeds':[3,4,5],'training_deadline_minutes_from_first_launch':610,
                    'research_pool_minutes':500}
                arms={n:{'encoder':'dinov2_vits14','image_size':336} for n in names}
                campaign.proposal={'arms':arms,'selection':{
                    'five_seed_stability_target':{'both_targets_pass_seeds_min':4}},
                    'analysis':{'paired_whole_group_bootstrap':{
                        'groups':2,'replicates':5,'seed':11}}}
                (campaign.root/'fixture.yaml').write_bytes(b'synthetic fixture')
                config_pin={'path':'fixture.yaml',
                            'sha256':hashlib.sha256(b'synthetic fixture').hexdigest()}
                items=[{'arm':a,'seed':s,'id':f'{a}-{s}','config':config_pin}
                       for s in range(1,6) for a in names]
                executed=[]

                def fake_execute(item, until, *, executed=executed, campaign=campaign, top=top):
                    self.assertGreater(until,time.time())
                    executed.append(item)
                    folder=campaign.base/item['id']
                    folder.mkdir()
                    (folder/'best.pt').write_bytes(b'synthetic model fixture')
                    (folder/'bundle.json').write_text('{"fixture":true}')
                    (folder/'calibration.json').write_text('{"fixture":true}')
                    ap=.99-top.index(item['arm'])*.01 if item['arm'] in top else .8
                    metric={'macro_ap':ap,'macro_masked_bce':.2,'calibrated_evaluation':{'targets':{
                        t:{'v11_quality_gate_pass':True,'ap':ap,'precision':.9,'recall':.9,
                           'fpr':.1,'f1':.9} for t in ['phone_use','looking_around']}}}
                    (folder/'metrics.json').write_text(json.dumps({'selection':metric}))
                    predictions=[{'sample_id':str(i),'group_id':str(i//2),
                        'targets':[i%2,i%2],'mask':[1,1],
                        'scores':[.9 if i%2 else .1]*2,'calibrated_thresholds':[.5,.5]}
                        for i in range(4)]
                    (folder/'predictions-selection.json').write_text(json.dumps(predictions))
                    campaign.state['runs'][item['id']]={'status':'FINISHED'}
                    campaign.state['research_runs'].append(item['id'])
                    return folder

                with patch.object(campaign,'plan',return_value={'items':items}), patch.object(
                    campaign,'sync',return_value={}), patch.object(
                        campaign,'execute',side_effect=fake_execute):
                    campaign.research()
                self.assertEqual(len(executed),expected_count)
                confirmation=set(top)|{'C0'}
                self.assertEqual({r['arm'] for r in executed if r['seed']>2},confirmation)
                for arm in confirmation:
                    self.assertEqual({r['seed'] for r in executed if r['arm']==arm},{1,2,3,4,5})
                summary=json.loads((campaign.base/'research-summary.json').read_text())
                self.assertEqual(summary['winner'],top[0])
                self.assertTrue(summary['four_of_five_both_targets'])
                handoff=summary['checkpoint_handoff']
                self.assertTrue((campaign.root/handoff['checkpoint']['path']).is_file())
                self.assertEqual(handoff['run_id'],f'{top[0]}-3')

    def test_incremental_verified_copy_restore_and_tamper_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/"source"
            source.mkdir()
            (source/"best.pt").write_bytes(b"model")
            (source/"config.json").write_text('{}')
            mirror = IncrementalMirror(root/"storage")
            until = time.time()+60
            first = mirror.sync([(source, "runs")], deadline=until)
            second = mirror.sync([(source, "runs")], deadline=until)
            self.assertEqual((first['copied_files'], second['copied_files']), (2, 0))
            self.assertEqual(second['skipped_files'], 2)
            fresh = root/"fresh"
            mirror.restore(root, {"runs":fresh})
            self.assertEqual((fresh/"best.pt").read_bytes(), b"model")
            (root/"storage/runs/best.pt").write_bytes(b"evil!")
            with self.assertRaises(DataContractError):
                IncrementalMirror(root/"storage").verify()

    def test_interrupted_publication_keeps_previous_committed_manifest_recoverable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/"campaign.json"
            source.write_text('{"epoch":1}')
            storage = root/"storage"
            mirror = IncrementalMirror(storage)
            mirror.sync([(source, "runs/campaign.json")], deadline=time.time()+60)
            source.write_text('{"epoch":22}')
            with patch('ai_exam_monitoring.training.campaign_runtime.write_json',
                       side_effect=OSError('simulated power loss before manifest commit')):
                with self.assertRaises(OSError):
                    mirror.sync([(source, "runs/campaign.json")], deadline=time.time()+60)
            recovered = IncrementalMirror(storage)
            recovered.verify()
            self.assertEqual(json.loads(recovered.verified_file('runs/campaign.json').read_text()),
                             {'epoch':1})
            recovered.restore(root, {'runs':root/'fresh'})
            self.assertEqual(json.loads((root/'fresh/campaign.json').read_text()), {'epoch':1})

    def test_persistence_refuses_escape_and_overwrite_of_local_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'file'
            source.write_text('input')
            mirror = IncrementalMirror(root/'storage')
            with self.assertRaises(DataContractError):
                mirror.sync([(source,'../escape')], deadline=time.time()+60)
            mirror.sync([(source,'runs/file')], deadline=time.time()+60)
            (root/'fresh').mkdir()
            (root/'fresh/file').write_text('local change')
            with self.assertRaises(DataContractError):
                mirror.restore(root, {'runs':root/'fresh'})

    def test_profile_and_original_phase_caps_never_reset_on_reconnect(self):
        proposal={'profiles':{'full':{'minimum_reported_vram_gib':40},
                              'core':{'minimum_reported_vram_gib':14}}}
        self.assertEqual(select_profile(80*1024**3,proposal),'full')
        self.assertEqual(select_profile(16*1024**3,proposal),'core')
        with self.assertRaises(DataContractError):
            select_profile(8*1024**3,proposal)
        budget={'setup_and_environment_minutes':40,'actual_gpu_smoke_minutes':70,
                'training_deadline_minutes_from_first_launch':610,'research_pool_minutes':500}
        self.assertEqual(phase_deadline(100,budget,'research',200),200+500*60)
        original=phase_deadline(100,budget,'smoke',100+20*60)
        self.assertEqual(original,100+90*60)
        with self.assertRaises(TimeoutError):
            admit_run(original-19*60,original,20*60,0,25)
        with self.assertRaises(TimeoutError):
            admit_run(100,10000,1200,25,25)
        with self.assertRaises(TimeoutError):
            admit_run(float('nan'),10000,1200,0,25)

    def test_rank_aggregates_seeds_support_before_AP_and_dedups_confirmation(self):
        def metric(passed, ap):
            return {'macro_ap':ap,'macro_masked_bce':.3,'calibrated_evaluation':{'targets':{
                t:{'v11_quality_gate_pass':passed,'precision':.9,'recall':.9,'fpr':.1}
                for t in ['phone_use','looking_around']}}}
        arms={'C0':{'encoder':'dinov2_vits14','image_size':336},
              'B':{'same_as':'C0','encoder':'dinov2_vitb14'}}
        stable=[metric(True,.8),metric(True,.8)]
        lucky=[metric(True,.99),metric(False,.99)]
        self.assertLess(recipe_key('C0',stable,arms),recipe_key('B',lucky,arms))
        self.assertLess(recipe_key('C0',stable,arms),recipe_key('B',stable,arms))
        self.assertEqual(representative_seed({1:stable[0],2:stable[1]}),1)
        self.assertEqual(len(set(['C0','B'])|{'C0'}),2)
        with self.assertRaises(DataContractError):
            resolve_arm({'cycle':{'same_as':'cycle'}},'cycle')

    def test_paired_group_bootstrap_is_fixed_threshold_and_self_delta_zero(self):
        rows=[{'sample_id':str(i),'group_id':str(i//2),'targets':[i%2,i%2],
               'mask':[1,1],'scores':[.9 if i%2 else .1]*2,
               'calibrated_thresholds':[.5,.5]} for i in range(8)]
        control={1:rows,2:rows}
        result=paired_group_bootstrap(control,control,replicates=100)
        self.assertFalse(result['threshold_refit'])
        for row in result['delta_candidate_minus_C0'].values():
            self.assertEqual(row['percentile_95'],[0.,0.])
            self.assertEqual(row['valid_replicates'],100)
        bad={1:[{**r,'group_id':'different'} for r in rows],2:rows}
        with self.assertRaises(DataContractError):
            paired_group_bootstrap(control,bad,replicates=2)
        self.assertTrue(tree_equal({'a':torch.tensor([1])},{'a':torch.tensor([1])}))
        self.assertFalse(tree_equal(torch.tensor([1]),torch.tensor([2])))
