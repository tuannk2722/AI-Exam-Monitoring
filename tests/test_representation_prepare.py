from __future__ import annotations

import importlib.util
import unittest
from dataclasses import asdict

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import test_dino_adaptation
    import yaml
    from fixtures.adaptation_fixture import pin

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.data.pilot_schema import read_records
    from ai_exam_monitoring.training.adaptation_config import load_adaptation_config
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.artifacts import code_identity, write_json
    from ai_exam_monitoring.training.representation_prepare import prepare


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class RepresentationPrepareTests(unittest.TestCase):
    def setUp(self):
        self.helper=test_dino_adaptation.DinoAdaptationTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root=self.helper.root
        self.config=self.helper.config()
        c=self.config
        records=read_records(self.root/c.cohorts[0].data.dataset/'manifest.jsonl')
        write_json(self.root/'pointer.json',{
            'package':c.cohorts[0].data.dataset,
            **{k:v for k,v in asdict(c.cohorts[0].data).items() if k!='dataset'}})
        write_json(self.root/'allocation.json',{'status':'owner_delegated_allocation','rows':[
            {'id':r.sample_id,'split':r.split,'group_id':r.group.leakage_group_id}
            for r in records]})
        write_json(self.root/'provenance.json',[
            {'id':r.sample_id,'cohort_origin':'synthetic_fixture','source_boundary':'fixture'}
            for r in records])
        expected={'train':6,'val':4,'test':0}
        write_json(self.root/'release-approved.json',{'decision':'accepted_local_release',
            'dataset_version':c.cohorts[0].data.dataset_version,'counts':expected})
        self.proposal={'dataset':{'expected_records':expected},'targets':c.target_order,
            'profiles':{'full':{'screening_arms':['C0','S4'],'smoke_arms':['C0','S4'],
                                'max_research_runs':10}},
            'budget':{'actual_gpu_smoke_minutes':70,
                      'per_research_run_including_reload_and_sync_minutes':20},
            'screening':{'seeds':[11,12]},'confirmation':{'additional_seeds':[13,14,15]},
            'smoke':{'epochs_per_run':5},
            'common':{'head':{'hidden_dim':c.head_hidden_dim,'dropout':c.head_dropout},
                      'head_learning_rate':.0003,'batch_size':2,'max_epochs':24,
                      'warmup_head_only_epochs':3,'pooling':'global_mean',
                      'augmentation':asdict(c.augmentation),
                      'loss':{'pos_weight':[1.,1.],'label_smoothing':.05}},
            'arms':{'C0':{'encoder':'dinov2_vits14','feature_dim':768,'image_size':28,
                          'train_last_blocks':2,'train_final_norm':True,
                          'backbone_learning_rate':.00001},
                    'S4':{'same_as':'C0','train_last_blocks':4}}}
        proposal_path=self.root/'proposal.yaml'
        proposal_path.write_text(yaml.safe_dump(self.proposal),encoding='utf-8')
        proposal_pin=asdict(pin(self.root,proposal_path))
        write_json(self.root/'authority.json',{'status':'approved','owner':c.owner,
            'proposal':proposal_pin,'final_test_inference_authorized':False,
            'cloud_upload_authorized':True,'cloud_providers':['Google Colab'],
            'implementation_authorized':True,'smoke_authorized':True,
            'research_authorized_after_smoke':True,
            'dataset_version':c.cohorts[0].data.dataset_version,
            'payload_sha256':c.cohorts[0].data.payload_sha256})
        self.design={'config_schema':'dinov2-adaptation-v6','run_prefix':'TINY',
            'authorization':asdict(pin(self.root,self.root/'authority.json')),
            'proposal':proposal_pin,'dataset_pointer':asdict(pin(self.root,self.root/'pointer.json')),
            'allocation':asdict(pin(self.root,self.root/'allocation.json')),
            'provenance':asdict(pin(self.root,self.root/'provenance.json')),
            'release_approval':asdict(pin(self.root,self.root/'release-approved.json')),
            'template':asdict(pin(self.root,self.root/'v4.yaml')),
            'config_dir':'outputs/configs','initialization_dir':'outputs/initialization',
            'smoke_receipt':'outputs/receipts/{profile}/gpu-smoke.json',
            'pretrained':{'dinov2_vits14':{'weights':asdict(c.weights),
                                          'license':asdict(c.weights_license),
                                          'source':asdict(c.encoder_source)}}}
        write_json(self.root/'design.json',self.design)

    def test_profile_materialization_strict_gates_and_native_crop_slices(self):
        design=self.root/'design.json'
        plan=prepare(design,self.root,'smoke',profile='full')
        self.assertEqual(len(plan['items']),4)
        config=load_adaptation_config(self.root/plan['items'][0]['config']['path'])
        cohorts,protocol=prepare_cohorts(config,self.root)
        for cohort in cohorts:
            expected=[r.sample_id for r in cohort.records if max(
                r.crop.context_box.xmax-r.crop.context_box.xmin,
                r.crop.context_box.ymax-r.crop.context_box.ymin)<=224]
            self.assertEqual(protocol['slice_enrollment'][cohort.name].get(
                'native_long_edge_le224',[]),expected)
        with self.assertRaises(DataContractError):
            prepare(design,self.root,'smoke',profile='full')
        with self.assertRaises(OSError):
            prepare(design,self.root,'research',profile='full')
        write_json(self.root/'outputs/receipts/full/gpu-smoke.json',{
            'status':'PASS','device':'cuda','profile':'full',
            'code_sha256':code_identity()['sha256'],
            'payload_sha256':self.config.cohorts[0].data.payload_sha256,
            'design_sha256':pin(self.root,design).sha256,
            'checks':{'resume':'PASS','reload':'PASS','stage_transition':'PASS'},
            'fixture_only_not_real_GPU_evidence':True})
        research=prepare(design,self.root,'research',profile='full')
        self.assertEqual(len(research['items']),10)
        self.assertEqual({r['seed'] for r in research['items']},{11,12,13,14,15})
        configs=[load_adaptation_config(self.root/r['config']['path']) for r in research['items']]
        heads={c.head_initialization.path for c in configs if c.seed==11}
        self.assertEqual(len(heads),1)
