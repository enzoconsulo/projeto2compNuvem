
const $ = (q)=>document.querySelector(q);

function rand(min,max){return Math.floor(Math.random()*(max-min+1))+min}
function clamp(n,min,max){return Math.max(min,Math.min(max,n))}

let cpu = rand(10,60);
let mem = rand(20,70);
let envs = rand(1,8);

function updateStats(){
  cpu = clamp(cpu + rand(-6,6), 0, 100);
  mem = clamp(mem + rand(-5,5), 0, 100);
  envs = clamp(envs + rand(-1,1), 0, 20);

  $("#statCPU").textContent = cpu + "%";
  $("#barCPU").style.width = cpu + "%";
  $("#statMEM").textContent = mem + "%";
  $("#barMEM").style.width = mem + "%";
  $("#statEnvs").textContent = envs;

  // Atualiza tabela fake
  const tbody = $("#tableBody");
  tbody.innerHTML = "";
  for(let i=0;i<Math.max(5, envs);i++){
    const status = ["Ativo","Aguardando","Erro"][rand(0,2)];
    const badge = status === "Ativo" ? "ok" : (status==="Erro"?"bad":"warn");
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>ambiente-${i+1}</td>
      <td><span class="badge ${badge}">${status}</span></td>
      <td>${clamp(cpu + rand(-10,10),0,100)}%</td>
      <td>${clamp(mem + rand(-10,10),0,100)}%</td>
      <td><button class="mini">Ver</button></td>
    `;
    tbody.appendChild(tr);
  }
}
setInterval(updateStats, 1200); updateStats();

// Toast & tema
$("#btnToast").addEventListener("click", ()=>{
  const t = $("#toast"); t.classList.add("show");
  setTimeout(()=>t.classList.remove("show"), 1600);
});
$("#btnTheme").addEventListener("click", ()=>{
  document.documentElement.classList.toggle("light");
});

// Animação simples no hero
$("#btnPulse").addEventListener("click", ()=>{
  const el = document.querySelector(".hero");
  el.animate([
    { transform:"scale(1)", boxShadow:"0 0 0 rgba(124,58,237,0)" },
    { transform:"scale(1.01)", boxShadow:"0 10px 40px rgba(124,58,237,.35)" },
    { transform:"scale(1)", boxShadow:"0 0 0 rgba(124,58,237,0)" },
  ], { duration:800, easing:"ease-in-out" });
});

// Gráfico minimalista em canvas
const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");
const W = canvas.width, H = canvas.height;
let data = new Array(60).fill(0).map(()=>rand(10,60));

function drawChart(){
  ctx.clearRect(0,0,W,H);
  // grid
  ctx.globalAlpha = 0.12;
  ctx.strokeStyle = "#aab4c3";
  for(let y=0; y<=H; y+=40){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
  ctx.globalAlpha = 1;

  // line
  ctx.beginPath();
  const step = W/(data.length-1);
  data.forEach((v,i)=>{
    const x = i*step;
    const y = H - (v/100)*H;
    if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  const grad = ctx.createLinearGradient(0,0,W,0);
  grad.addColorStop(0,"#7c3aed"); grad.addColorStop(1,"#22d3ee");
  ctx.strokeStyle = grad;
  ctx.lineWidth = 3;
  ctx.stroke();

  // fill
  ctx.lineTo(W,H); ctx.lineTo(0,H); ctx.closePath();
  const g2 = ctx.createLinearGradient(0,0,0,H);
  g2.addColorStop(0,"rgba(124,58,237,.25)"); g2.addColorStop(1,"rgba(34,211,238,.05)");
  ctx.fillStyle = g2;
  ctx.fill();
}

setInterval(()=>{
  data.push(cpu); data.shift(); drawChart();
}, 800);
drawChart();
