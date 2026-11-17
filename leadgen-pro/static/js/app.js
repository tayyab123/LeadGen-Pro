const state = { leads: [], allLeads: [], selected: new Set(), page: 1, pageSize: 8, searches: 0, savedMode: false };
const $ = (id) => document.getElementById(id);
let map, markers;
const fields = ["name","category","address","phone","website","place_id","lat","lon","opening_hours"];

function toast(message, type="success") {
  const item = document.createElement("div");
  item.className = `toast ${type}`;
  item.innerHTML = `<i class="bi ${type === "error" ? "bi-exclamation-circle" : "bi-check-circle"}"></i><span></span>`;
  item.querySelector("span").textContent = message;
  $("toastContainer").appendChild(item);
  setTimeout(() => { item.style.opacity="0"; item.style.transform="translateX(15px)"; setTimeout(()=>item.remove(),250); }, 3600);
}
function animateNumber(element, target) {
  const start = Number(element.textContent.replace(/,/g,"")) || 0, duration = 550, begin = performance.now();
  function tick(now) {
    const progress = Math.min((now-begin)/duration,1), eased = 1-Math.pow(1-progress,3);
    element.textContent = Math.round(start+(target-start)*eased).toLocaleString();
    if(progress<1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
function updateStats() {
  const data = state.allLeads;
  animateNumber($("statFound"), data.length);
  animateNumber($("statSearches"), state.searches);
  animateNumber($("statWebsites"), data.filter(x=>x.website && x.website!=="Not Available").length);
  animateNumber($("statPhones"), data.filter(x=>x.phone && x.phone!=="Not Available").length);
  $("sideLeadCount").textContent = data.length;
}
function normalizeUrl(url) {
  if (!url || url === "Not Available") return null;
  return /^https?:\/\//i.test(url) ? url : `https://${url}`;
}
function filteredLeads() {
  const query = $("tableSearch").value.toLowerCase().trim();
  const filter = $("contactFilter").value;
  return state.leads.filter(lead => {
    const matches = fields.some(key => String(lead[key] ?? "").toLowerCase().includes(query));
    const hasWebsite = lead.website && lead.website !== "Not Available";
    const hasPhone = lead.phone && lead.phone !== "Not Available";
    return matches && (filter==="all" || (filter==="website" && hasWebsite) || (filter==="phone" && hasPhone));
  });
}
function renderTable() {
  const rows = filteredLeads(), pages = Math.max(1,Math.ceil(rows.length/state.pageSize));
  state.page = Math.min(state.page,pages);
  const start=(state.page-1)*state.pageSize, visible=rows.slice(start,start+state.pageSize);
  $("resultCount").textContent = rows.length;
  $("showingText").textContent = `Showing ${rows.length ? start+1 : 0}–${Math.min(start+state.pageSize,rows.length)} of ${rows.length} businesses`;
  $("pageText").textContent = `${state.page} / ${pages}`;
  $("prevPage").disabled=state.page===1; $("nextPage").disabled=state.page===pages;
  $("selectAll").checked = visible.length>0 && visible.every(x=>state.selected.has(x.place_id));
  if (!visible.length) {
    $("leadsBody").innerHTML = `<tr class="empty-row"><td colspan="7"><div class="empty-state"><div class="empty-illustration"><i class="bi bi-search"></i></div><strong>No matching businesses</strong><p>Try changing your search or filters.</p></div></td></tr>`;
    return;
  }
  $("leadsBody").innerHTML = visible.map((lead,index)=>{
    const checked=state.selected.has(lead.place_id)?"checked":"";
    const website=normalizeUrl(lead.website);
    const phone=lead.phone && lead.phone!=="Not Available" ? `<a class="contact-link" href="tel:${escapeHtml(lead.phone)}">${escapeHtml(lead.phone)}</a>` : `<span class="muted-cell">Not available</span>`;
    const web=website?`<a class="contact-link" href="${escapeHtml(website)}" target="_blank" rel="noopener">Visit site <i class="bi bi-box-arrow-up-right"></i></a>`:`<span class="muted-cell">Not available</span>`;
    const mapLink=lead.lat!=null&&lead.lon!=null?`<a class="map-link" target="_blank" rel="noopener" href="https://www.openstreetmap.org/?mlat=${lead.lat}&mlon=${lead.lon}#map=17/${lead.lat}/${lead.lon}" title="Open map"><i class="bi bi-geo-alt-fill"></i></a>`:"—";
    return `<tr style="animation:rise .3s ${index*25}ms both"><td><input type="checkbox" class="row-check" data-id="${escapeHtml(lead.place_id)}" ${checked}></td><td><div class="business-cell"><div class="business-avatar"><i class="bi bi-building"></i></div><div><strong title="${escapeHtml(lead.name)}">${escapeHtml(lead.name)}</strong><small>${escapeHtml(lead.place_id || "Geoapify place")}</small></div></div></td><td><span class="category-tag">${escapeHtml((lead.category||"Business").split(",").slice(-1)[0])}</span></td><td title="${escapeHtml(lead.address)}">${escapeHtml(lead.address||"Not Available")}</td><td>${phone}</td><td>${web}</td><td>${mapLink}</td></tr>`;
  }).join("");
  document.querySelectorAll(".row-check").forEach(input=>input.addEventListener("change",()=>{
    if(input.checked) state.selected.add(input.dataset.id); else state.selected.delete(input.dataset.id);
    $("selectAll").checked=visible.every(x=>state.selected.has(x.place_id));
  }));
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
}
async function api(url, options={}) {
  const response=await fetch(url,{headers:{"Content-Type":"application/json"},...options});
  const type=response.headers.get("content-type")||"";
  if(!response.ok){let msg="Request failed."; if(type.includes("application/json")){const body=await response.json();msg=body.error||msg;}else msg=await response.text();throw new Error(msg);}
  return response;
}
async function runSearch(event) {
  event.preventDefault();
  const keyword=$("keyword").value.trim(), location=$("location").value.trim();
  if(!keyword||!location){toast("Please enter a business category and location.","error");return;}
  const button=$("searchBtn"); button.disabled=true; button.innerHTML='<span class="spinner-border spinner-border-sm"></span> Searching…';
  $("resultSubtitle").textContent="Searching Geoapify for matching businesses…";
  $("leadsBody").innerHTML=`<tr><td colspan="7"><div class="skeleton"></div></td></tr>`;
  try {
    const response=await api("/api/search",{method:"POST",body:JSON.stringify({keyword,location,radius:$("radius").value,limit:$("limit").value})});
    const result=await response.json();
    state.leads=result.leads||[]; state.allLeads=state.leads.slice(); state.selected.clear(); state.searches++; state.page=1; state.savedMode=false;
    $("resultSubtitle").textContent=`${state.leads.length} businesses found near ${result.location}.`;
    renderTable(); updateStats(); updateMap(state.leads);
    toast(`${state.leads.length} businesses found successfully.`);
    if(!state.leads.length) toast("No businesses were returned. Try a broader category or radius.","error");
  } catch(error) {
    $("leadsBody").innerHTML=`<tr class="empty-row"><td colspan="7"><div class="empty-state"><div class="empty-illustration"><i class="bi bi-exclamation-triangle"></i></div><strong>Search couldn't be completed</strong><p>${escapeHtml(error.message)}</p></div></td></tr>`;
    $("resultSubtitle").textContent="Search failed. No sample data has been displayed.";
    toast(error.message,"error");
  } finally {button.disabled=false;button.innerHTML='<i class="bi bi-search"></i><span>Find businesses</span>';}
}
function initMap() {
  if(!window.L) return;
  map=L.map("map",{scrollWheelZoom:false}).setView([31.5204,74.3587],11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'}).addTo(map);
  markers=L.featureGroup().addTo(map);
}
function updateMap(leads) {
  if(!map) return;
  markers.clearLayers();
  const points=leads.filter(x=>Number.isFinite(Number(x.lat))&&Number.isFinite(Number(x.lon)));
  points.forEach(lead=>L.marker([lead.lat,lead.lon]).bindPopup(`<strong>${escapeHtml(lead.name)}</strong><br>${escapeHtml(lead.address)}`).addTo(markers));
  if(points.length) map.fitBounds(markers.getBounds().pad(.15),{maxZoom:14});
}
async function loadSaved() {
  try {
    const response=await api("/api/leads"); const data=await response.json();
    state.leads=data.leads||[];state.allLeads=state.leads.slice();state.selected.clear();state.page=1;state.savedMode=true;
    $("resultSubtitle").textContent=`${data.count} saved leads in your local database.`;
    renderTable();updateStats();updateMap(state.leads);toast("Saved leads loaded.");
  } catch(error){toast(error.message,"error");}
}
async function exportLeads(format) {
  const selected=state.selected.size?state.leads.filter(x=>state.selected.has(x.place_id)):state.leads;
  if(!selected.length){toast("There are no leads to export.","error");return;}
  try {
    const response=await api(`/api/export/${format}`,{method:"POST",body:JSON.stringify({leads:selected})});
    const blob=await response.blob(),url=URL.createObjectURL(blob),a=document.createElement("a");
    a.href=url;a.download=`leadgen-pro-leads.${format==="excel"?"xlsx":"csv"}`;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
    toast(`${selected.length} leads exported to ${format.toUpperCase()}.`);
  }catch(error){toast(error.message,"error");}
}
async function checkConfig() {
  try{const response=await api("/api/config/status"),data=await response.json();$("apiStatus").textContent=data.configured?"Geoapify API configured":"Add your Geoapify API key";$("apiStatus").previousElementSibling.style.background=data.configured?"#36bd91":"#f5a623";}
  catch{$("apiStatus").textContent="API status unavailable";}
}
$("searchForm").addEventListener("submit",runSearch);
$("tableSearch").addEventListener("input",()=>{state.page=1;renderTable();});
$("contactFilter").addEventListener("change",()=>{state.page=1;renderTable();});
$("prevPage").addEventListener("click",()=>{state.page--;renderTable();});
$("nextPage").addEventListener("click",()=>{state.page++;renderTable();});
$("selectAll").addEventListener("change",event=>{
  const visible=filteredLeads().slice((state.page-1)*state.pageSize,state.page*state.pageSize);
  visible.forEach(x=>event.target.checked?state.selected.add(x.place_id):state.selected.delete(x.place_id));renderTable();
});
$("csvBtn").addEventListener("click",()=>exportLeads("csv"));
$("excelBtn").addEventListener("click",()=>exportLeads("excel"));
$("savedBtn").addEventListener("click",loadSaved);
$("themeBtn").addEventListener("click",()=>{
  document.body.classList.toggle("dark");
  $("themeBtn").innerHTML=document.body.classList.contains("dark")?'<i class="bi bi-sun"></i>':'<i class="bi bi-moon-stars"></i>';
  setTimeout(()=>map&&map.invalidateSize(),100);
});
$("menuBtn").addEventListener("click",()=>{$("sidebar").classList.add("open");$("overlay").classList.add("show");});
$("overlay").addEventListener("click",()=>{$("sidebar").classList.remove("open");$("overlay").classList.remove("show");});
document.querySelectorAll(".nav-link").forEach(link=>link.addEventListener("click",()=>{$("sidebar").classList.remove("open");$("overlay").classList.remove("show");}));
initMap();checkConfig();
