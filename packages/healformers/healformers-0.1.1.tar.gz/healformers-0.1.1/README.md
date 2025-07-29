# 🌌 HealFormers: Mask-Aware HEALPix Transformers

<p align="center">
  <img src="./imgs/healformer_architecture.jpg"  alt="architecture" width="500">
</p>

**HealFormer** is a cutting-edge transformer model specifically designed for data structured on the **HEALPix grid**, widely used in **cosmology**, **astrophysics**, and **large-scale structure analysis**. HealFormer natively manages incomplete sky observations with state-of-the-art precision, eliminating the need for projections or specialized spherical convolutions, and scales effortlessly to large astronomical surveys.

> [!NOTE]  
>
> * Source code will be publicly available after paper acceptance.
> * Pretrained models and datasets will be hosted on [🤗 HuggingFace](https://huggingface.co/).

---

## 🌠 Why Choose HealFormer?

Traditional spherical analysis methods often struggle with partial-sky coverage and computational efficiency. HealFormer is uniquely designed to solve these challenges:

| 🚩 Pain Points                        | 🎯 HealFormer Solutions                              |
| ------------------------------------- | ---------------------------------------------------   |
| Inefficient mask handling             | ✅ Direct mask-aware learning                        |
| Distortion from projections           | ✅ Native HEALPix operations (no projections needed) |
| Poor scalability for high resolutions | ✅ Efficient from Nside=256 up to Nside=1024+        |
| Expensive model training              | ✅ LoRA-based tuning reduces cost by 90%+            |
| Limited generalization                | ✅ Strong transfer learning and generalization       |

---

## 🌟 Key Features

* **Mask Awareness:** Directly processes masked regions; adapts to arbitrary mask sizes and shapes.
* **Native HEALPix Integration:** No need for projection or spherical approximation; maintains full data integrity.
* **State-of-the-Art Performance:** Exceeds Wiener filter and Kaiser-Squires both in pixel space and harmonic space.
* **Unified Masking:** A single model supports various mask patterns and sky coverage (e.g. KiDS, DES, DECaLS, Planck), without retraining.
* **Efficient Transfer Learning:** LoRA-based fine-tuning reduces trainable parameters to ~10%, enabling efficient transfer learning.
* **Scalable & Generalizable:** Efficiently scales from low (Nside=256) to high (Nside=1024+) resolutions; generalizes robustly across different cosmological parameters.

---

## 📦 Installation

Install HealFormer easily via pip:

```bash
pip install healformers
```

Requirements: Python 3.11+, healpy, torch, transformers, etc. (See `pyproject.toml` for details)

---

## 🚀 Quickstart Example: Weak-Lensing Mass Mapping

Minimal working example to reconstruct a kappa map:

```python
import healpy as hp
import torch
from healformers import HealFormerModel, Mock

# Generate mock data (gamma1, gamma2)
batch = Mock.generate_full_batch(
    nside=256, mask_type="decals", batch_size=1, return_type="torch"
)
kappa_true = batch["targets"][0, -1]

# Load pretrained model
model_path = "path_to_model_directory"
model = HealFormerModel.from_pretrained(model_path)

# Predict kappa map
with torch.no_grad():
    kappa_pred = model(**batch)["logits"][0, 0]

# Visualization
hp.mollview(kappa_true.numpy(), nest=True, title="True Kappa", sub=(121))
hp.mollview(kappa_pred.numpy(), nest=True, title="Reconstructed Kappa", sub=(122))
```

---

## 🛰️ Scientific Applications

- **Weak lensing mass mapping** under realistic, incomplete sky coverage – ✅ **Ready**
- **Power spectrum estimation** on irregular spherical masks – 🔜 *Coming soon*
- **Field-level cosmological inference** from partial-sky data – 🔜 *Coming soon*

---

## 🎨 Visualization Showcase

**1. Clean Map Reconstruction (w/ mask)**

*Kaiser-Squires (KS) vs Wiener filter (WF) vs HealFormer (HF)*

<p align="center">
  <img src="./imgs/mask_effect_nside256_maskDECaLS_noiseFalse.jpg"  alt="mask_effect" width="500">
</p>

**2. Noisy Map Reconstruction**

<p align="center">
  <img src="./imgs/noise_effect_nside256_maskDECaLS_noiseTrue.jpg"  alt="noise_effect" width="500">
</p>

**3. Residuals Across Diverse Masks**

<p align="center">
  <img src="./imgs/compare_allMask_residual_nside256.jpg"  alt="residual_allMask" width="500">
</p>

---

## 🧩 Model Zoo & Resources

* 📦 **Pretrained models:** *Coming soon*
* 📚 **Fine-tuning guides:** *Coming soon*

---

## 📄 Citation

If you utilize HealFormer, please cite:

```
[Your citation here after publication]
```

---

## 🤝 Contribution & Community

We warmly welcome contributions, feedback, and bug reports!

* Open an issue on [GitHub Issues](https://github.com/lalalabox/healformers/issues)
* Submit pull requests for direct contributions.

---

## ⚙️ Built With

Special thanks to frameworks and models enabling this work:

* [**PyTorch**](https://pytorch.org/)
* [**🤗 Transformers & PEFT (LoRA)**](https://github.com/huggingface/transformers)
* [**Masked Autoencoders (MAE)**](https://github.com/facebookresearch/mae)

---

## 📜 License

Licensed under **Apache-2.0**. See [LICENSE](https://github.com/lalalabox/healformers/blob/main/LICENSE) for details.
