const modules = [
  {
    title: "NiChart",
    image: "images/nichart_logo_v2_img1_v2.png",
    short: "Neuroimaging Chart of AI-based imaging biomarkers",
    full: `
      A framework to:
      • Process MRI images
      • Harmonize scans
      • Apply ML models
      • Derive personalized biomarkers
    `
  },
  {
    title: "MRI Segmentation",
    image: "images/nichart_logo_v2_img4_v2.png",
    short: "Deep-learning segmentation of healthy and pathological anatomy",
    full: `
      • DLICV
      • DLMUSE
      • DLWMLS
    `
  },
  {
    title: "AI Biomarkers",
    image: "images/nichart_logo_v2_img3_v2.png",
    short: "AI-based biomarkers of brain aging and disease",
    full: `
      • SPARE-BA / DeepSPARE-BA
      • SPARE-AD
      • Cardiometabolic & psychiatric models
    `
  },
  {
    title: "Brain Aging Dimensions",
    image: "images/nichart_logo_v2_img5_v2.png",
    short: "Data-driven indices of aging heterogeneity",
    full: `
      • Surreal-GAN R1–R5
      • CCL-NMF longitudinal models
    `
  },
  {
    title: "Abnormality Maps",
    image: "images/nichart_logo_v2_img6_v2.png",
    short: "Voxelwise CSF abnormality maps",
    full: `
      • RAVENS-based density maps
      • Individualized regional deviations
    `
  }
];

let index = 0;
const carousel = document.getElementById("carousel");

function render() {
  carousel.innerHTML = modules.map(m => `
    <div class="card">
      <img src="${m.image}" alt="${m.title}">
      <div>
        <h2>${m.title}</h2>
        <p class="short">${m.short}</p>
        <details>
          <summary>Learn more</summary>
          <p>${m.full.replace(/\n/g, "<br>")}</p>
        </details>
      </div>
    </div>
  `).join("");
}

function update() {
  carousel.style.transform = `translateX(-${index * 100}%)`;
}

function next() {
  index = Math.min(index + 1, modules.length - 1);
  update();
}

function prev() {
  index = Math.max(index - 1, 0);
  update();
}

window.addEventListener("wheel", e => {
  if (e.deltaY > 0) next();
  else prev();
});

render();
update();
