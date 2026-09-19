const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", ""]);
const API_BASE = LOCAL_HOSTS.has(window.location.hostname)
  ? "http://127.0.0.1:8000"
  : "https://atslens.onrender.com";

let currentReportUrl = null;
const $ = (id) => document.getElementById(id);

async function checkHealth(){
  const status=$("status");
  try{
    const res=await fetch(`${API_BASE}/v3/health`);
    const data=await res.json();
    if(!res.ok) throw new Error();
    const backend=data.semantic_backend?.backend || "unknown";
    status.textContent=`Backend online • ${backend}`;
    status.className="status online";
  }catch{
    status.textContent="Backend offline";
    status.className="status offline";
  }
}

function setScore(id,value){$(id).textContent=Math.round(Number(value)||0)}
function pill(text){return `<span class="pill">${String(text||"none")}</span>`}
function esc(value){return String(value??"").replace(/[&<>'"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]))}

function render(data){
  const s=data.scores||{};
  setScore("overall",s.overall_score);setScore("job",s.job_match_score);setScore("ats",s.ats_compatibility_score);setScore("quality",s.resume_quality_score);setScore("confidence",s.analysis_confidence);
  const hybrid=data.hybrid_matching||{};
  $("matchSummary").textContent=`${hybrid.matched_count||0} matched • ${hybrid.missing_count||0} missing`;
  $("requirements").innerHTML=(hybrid.matches||[]).map(x=>`<tr><td><strong>${esc(x.skill)}</strong></td><td>${esc(x.priority)}</td><td>${pill(x.match_type)}</td><td>${Math.round((x.match_score||0)*100)}%</td></tr>`).join("");

  const evidence=(data.evidence_intelligence?.skills||[]).filter(x=>x.matched).sort((a,b)=>(b.evidence_quality||0)-(a.evidence_quality||0)).slice(0,8);
  $("evidence").innerHTML=evidence.length?evidence.map(x=>`<div class="item"><strong>${esc(x.skill)} • ${Math.round((x.evidence_quality||0)*100)}%</strong><p>${esc(x.source_section||"Unknown section")} • ${esc(x.recency?.label||"date unknown")}<br>${esc(x.evidence||"Evidence localized through matching signals.")}</p></div>`).join(""):"<div class='item'><p>No matched evidence available.</p></div>";

  const rel=data.reliability||{};
  const keyword=rel.keyword_stuffing||{}, timeline=rel.timeline||{}, contradictions=rel.contradictions||{};
  $("reliability").innerHTML=`
    <div class="item"><strong>Keyword stuffing risk: ${keyword.risk_score||0}/100</strong><p>${keyword.flagged?"Review repeated skill keywords.":"No strong stuffing signal detected."}</p></div>
    <div class="item"><strong>Timeline issues: ${timeline.issue_count||0}</strong><p>${esc(timeline.status||"")}</p></div>
    <div class="item"><strong>Explicit contradictions: ${contradictions.issue_count||0}</strong><p>${esc(contradictions.status||"")}</p></div>`;

  const suggestions=data.explanation?.suggestions||[];
  $("suggestions").innerHTML=suggestions.length?suggestions.map(x=>`<li>${esc(x)}</li>`).join(""):"<li>No suggestion generated.</li>";
  $("researchNote").textContent=(data.limitations||[]).join(" ");
  $("results").classList.remove("hidden");
  $("results").scrollIntoView({behavior:"smooth",block:"start"});

  if(data.pdf_url){currentReportUrl=`${API_BASE}${data.pdf_url}`;$("download").disabled=false}
}

$("analyze").addEventListener("click",async()=>{
  const file=$("resume").files[0], jd=$("jd").value.trim();
  if(!file){alert("Please upload a resume.");return}
  if(!jd){alert("Please paste the job description.");return}
  const fd=new FormData();
  fd.append("file",file);fd.append("job_description",jd);fd.append("candidate_type",$("candidateType").value);fd.append("target_field",$("targetField").value);fd.append("experience_years",$("experienceYears").value||"0");fd.append("preferred_role",$("preferredRole").value||"");fd.append("target_company",$("targetCompany").value||"MNC");
  const btn=$("analyze");btn.disabled=true;btn.textContent="Analyzing…";
  try{
    const res=await fetch(`${API_BASE}/analyze-v3`,{method:"POST",body:fd});
    const data=await res.json();
    if(!res.ok) throw new Error(data.detail||"Analysis failed");
    render(data);
  }catch(err){alert(`Analysis Error: ${err.message}`)}finally{btn.disabled=false;btn.textContent="Analyze with V3"}
});

$("download").addEventListener("click",()=>{if(currentReportUrl) window.open(currentReportUrl,"_blank")});
checkHealth();
