/* Offline owner draft only. No network, no label inference, no dataset writes. */
"use strict";
const A = window.AUDIT, $ = id => document.getElementById(id);
const records = new Map(A.records.map(r => [r.id,r]));
const groups = new Map(A.groups.map(g => [g.id,g]));
const order = A.groups.flatMap(g => g.members), storageKey = "crop-audit:" + A.cohort;
const fields = ["phone","looking","action","flag","angle","tags","note","done"];
let state = {schema:"crop-review-draft-v1",cohort:A.cohort,decisions:{},groupNotes:{}}, page=0,current=order[0],filtered=[],storageBlocked=false;
function validate(value){
  if(!value || value.schema!==state.schema || value.cohort!==A.cohort || !value.decisions || !value.groupNotes || Array.isArray(value.decisions) || Array.isArray(value.groupNotes))throw Error("Sai định dạng hoặc cohort; chưa nhập dữ liệu.");
  for(const [id,d] of Object.entries(value.decisions)){
    if(!records.has(id)||!d||d.sha256!==records.get(id).sha256)throw Error("Sai ID/SHA: "+id);
    for(const k of ["phone","looking"])if(!["","P","N","U"].includes(d[k]))throw Error("Nhãn không hợp lệ: "+id);
    if(!["","keep","recrop","remove","unsure"].includes(d.action)||typeof d.flag!=="boolean"||typeof d.done!=="boolean")throw Error("Quyết định không hợp lệ: "+id);
    for(const k of ["angle","tags","note"])if(typeof d[k]!=="string")throw Error("Ghi chú không hợp lệ: "+id);
    if(!["","Trước","Bên / chéo","Sau","Trên cao","Không rõ"].includes(d.angle))throw Error("Góc nhìn không hợp lệ");
    if(d.done && (!d.action || (d.action!=="remove" && (!d.phone || !d.looking))))throw Error("Review chưa đủ trường: "+id);
  }
  for(const [id,note] of Object.entries(value.groupNotes))if(!groups.has(id)||typeof note!=="string")throw Error("Ghi chú nhóm không hợp lệ");
  return value;
}
function status(text,error=false){$("saveStatus").textContent=text;$("saveStatus").classList.toggle("error",error);}
try{const saved=localStorage.getItem(storageKey);if(saved)state=validate(JSON.parse(saved));}catch(e){storageBlocked=true;status("Không đọc được nháp cũ; hãy xuất JSON trước khi đóng",true);}
function persist(){state.updatedAt=new Date().toISOString();if(storageBlocked){status("Chưa lưu browser — hãy xuất JSON",true);return;}try{localStorage.setItem(storageKey,JSON.stringify(state));status("Đã lưu nháp trên browser");}catch(e){status("Không lưu được — hãy xuất JSON",true);}}
function decision(id){return state.decisions[id]||{sha256:records.get(id).sha256,phone:"",looking:"",action:"",flag:false,angle:"",tags:"",note:"",done:false};}
function matches(id){const r=records.get(id),d=decision(id),f=$("filter").value,q=$("search").value.toLowerCase().trim();return (!$("group").value||r.group===$("group").value)&&(!q||[id,d.note,d.tags,d.angle].join(" ").toLowerCase().includes(q))&&({all:true,todo:!d.done,done:d.done,flag:d.flag,recrop:d.action==="recrop",remove:d.action==="remove",upscale:r.scale>1}[f]);}
function progress(){const done=Object.values(state.decisions).filter(d=>d.done).length;$("progress").textContent=`${done} / ${A.records.length} đã chốt`;}
function renderList(){filtered=order.filter(matches);page=Math.min(page,Math.max(0,Math.ceil(filtered.length/12)-1));$("tiles").replaceChildren();
  for(const id of filtered.slice(page*12,page*12+12)){const r=records.get(id),d=decision(id),b=document.createElement("button");b.className="tile"+(id===current?" active":"");b.dataset.id=id;b.title=id;const img=document.createElement("img");img.src=r.original;img.alt=id;img.loading="lazy";const name=document.createElement("small");name.textContent=id;const badge=document.createElement("span");badge.className="badge";badge.textContent=(d.done?"✓ ":"")+(d.flag?"★":"");b.append(img,name,badge);b.onclick=()=>select(id);$("tiles").append(b);}
  $("count").textContent=filtered.length+" crop";$("page").textContent=`${filtered.length?page+1:0} / ${Math.ceil(filtered.length/12)}`;$("prevPage").disabled=page===0;$("nextPage").disabled=(page+1)*12>=filtered.length;
  const g=groups.get($("group").value);$("groupTitle").textContent=g?g.title:"Toàn bộ · thứ tự tương đồng";$("groupHint").textContent=g?g.note:"Chọn một nhóm để ghi chú chung. Tìm kiếm không lọc theo nguồn hoặc split cũ.";$("groupNote").disabled=!g;$("groupNote").value=g?(state.groupNotes[g.id]||""):"";progress();}
function select(id){current=id;const r=records.get(id),d=decision(id);$("sampleId").textContent=id+" · "+r.group;$("original").src=r.original;$("originalLink").href=r.original;$("prepared").src=r.input;$("dimensions").textContent=`${r.width} × ${r.height}`;$("scale").textContent=`${r.scale>1?"Phóng":"Thu / giữ"} ${r.scale.toFixed(2)}× · không augmentation`;
  const s=224/Math.max(r.width,r.height),w=r.width*s,h=r.height*s,a=r.anchor;Object.assign($("anchorBox").style,{left:((224-w)/2+a[0]*w)+"px",top:((224-h)/2+a[1]*h)+"px",width:((a[2]-a[0])*w)+"px",height:((a[3]-a[1])*h)+"px"});$("anchorBox").hidden=!$("showAnchor").checked;
  $("suggestion").textContent=r.suggestion;const label=x=>x===null?"U":x===1?"P":"N";$("old").textContent=`Cũ: ${r.old_usage} · Phone ${label(r.old_labels[0])} / Looking ${label(r.old_labels[1])} · ${r.source} · lineage ${r.lineage||"chưa có"}`+(r.blockers.length?" · Blockers: "+r.blockers.join(", "):"");$("old").hidden=!$("showOld").checked;
  for(const k of fields){if(["flag","done"].includes(k))$(k).checked=d[k];else $(k).value=d[k];}$("draftState").textContent=d.done?"Đã chốt trong bản review nháp; V12 chưa thay đổi.":"Chưa chốt; mọi lựa chọn là bản nháp.";renderList();}
function capture(changed){let d=decision(current);for(const k of fields)d[k]=["flag","done"].includes(k)?$(k).checked:$(k).value;
  if(!["done","flag"].includes(changed)){d.done=false;$("done").checked=false;}
  if(d.done&&(!d.action||(d.action!=="remove"&&(!d.phone||!d.looking)))){d.done=false;$("done").checked=false;alert("Chọn xử lý crop và cả hai nhãn trước khi chốt. Đề xuất loại không bắt buộc có nhãn.");}
  d.updatedAt=new Date().toISOString();state.decisions[current]=d;persist();renderList();$("draftState").textContent=d.done?"Đã chốt trong bản review nháp; V12 chưa thay đổi.":"Chưa chốt; mọi lựa chọn là bản nháp.";
}
function move(delta){const pool=filtered.length?filtered:order;const i=pool.indexOf(current);const next=Math.max(0,Math.min(pool.length-1,i+delta));page=Math.floor(next/12);select(pool[next]);}
for(const g of [{id:"",title:`Tất cả ${A.records.length} crop`},...A.groups]){const op=document.createElement("option");op.value=g.id;op.textContent=g.title+(g.members?` (${g.members.length})`:"");$("group").append(op);}
for(const k of fields)$(k).addEventListener(["note","tags"].includes(k)?"input":"change",()=>capture(k));
for(const id of ["group","filter","search"])$(id).addEventListener(id==="search"?"input":"change",()=>{page=0;renderList();if(filtered.length)select(filtered[0]);});
$("showOld").onchange=()=>{$("old").hidden=!$("showOld").checked;};
$("showAnchor").onchange=()=>{$("anchorBox").hidden=!$("showAnchor").checked;};
$("prev").onclick=()=>move(-1);$("next").onclick=()=>move(1);
$("prevPage").onclick=()=>{page--;renderList();};$("nextPage").onclick=()=>{page++;renderList();};
$("nextTodo").onclick=()=>{const pool=order.filter(id=>(!$("group").value||records.get(id).group===$("group").value)&&!decision(id).done);if(!pool.length){alert("Không còn crop chưa chốt trong nhóm đang chọn.");return;}const position=order.indexOf(current),id=pool.find(id=>order.indexOf(id)>position)||pool[0];$("filter").value="todo";$("search").value="";filtered=order.filter(matches);page=Math.floor(filtered.indexOf(id)/12);select(id);};
$("groupNote").oninput=()=>{if($("group").value){state.groupNotes[$("group").value]=$("groupNote").value;persist();}};
$("export").onclick=()=>{const value={...state,exportedAt:new Date().toISOString(),inventory:A.records.map(r=>({id:r.id,sha256:r.sha256}))};const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="v12-review-"+new Date().toISOString().replace(/[:.]/g,"-")+".json";a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);status("Đã yêu cầu tải JSON; kiểm tra Downloads");};
$("import").onchange=async event=>{const file=event.target.files[0];if(!file)return;try{const next=validate(JSON.parse(await file.text()));if(confirm("Thay toàn bộ nháp đang mở bằng file này? Hãy xuất nháp hiện tại trước nếu cần giữ.")){state=next;storageBlocked=false;persist();select(current);}}catch(e){alert("Không nhập: "+e.message);}event.target.value="";};
document.addEventListener("keydown",e=>{if(["INPUT","TEXTAREA","SELECT"].includes(e.target.tagName)||$("helpDialog").open)return;if(e.key==="ArrowLeft"||e.key==="ArrowRight"){e.preventDefault();move(e.key==="ArrowLeft"?-1:1);}});
$("scope").textContent=`Đủ ${A.records.length} accepted crop, gồm review-only và test cũ. Không loại ảnh theo split. Nhãn cũ ẩn mặc định. Test đã được mở cho đợt audit này; chưa có split/holdout mới.`;
$("help").onclick=()=>$("helpDialog").showModal();$("closeHelp").onclick=()=>$("helpDialog").close();
select(current);
// Expose pure validation for offline regression tests; it cannot apply reviews to data.
window.reviewValidation=validate;
