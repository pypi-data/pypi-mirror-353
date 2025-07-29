[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://github.com/AspirinCode/QRCI)


# QRCI

**A Quantitative Ring Complexity Index for Profiling Ring Topology and Chemical Diversity** 

![QRCI](https://raw.githubusercontent.com/AspirinCode/qrci/main/figures/qrci_cover.png)

$\mathrm{QRCI}=\frac{\mathrm{TRS}}{N_{\mathrm{ra}}}\left(1+\frac{N_{\mathrm{fr}}}{N_{\mathrm{r}}+1}\right)+\sum_{r}\left[\frac{360}{360-\alpha_{\mathrm{ideal}}(\ell_{r})}\cdot\frac{1}{\ell_{r}}\cdot\lambda_{M}(\ell_{r})\right]+\frac{\sum W_{i}\cdot D_{i}}{\sqrt{N_{\mathrm{ra}}\cdot\mathrm{TRS}}}+\frac{\log(N_{\mathrm{ta}})}{N_{\mathrm{r}}+1}+W_{m}\cdot\frac{N_{\mathrm{mr}}}{N_{\mathrm{r}}+1}$  

* **TRS** (Total Ring Size): Sum of all ring sizes.
* **$N_{\mathrm{ra}}$**: Total number of atoms in all rings.
* **$N_{\mathrm{r}}$**: Total number of rings
* **$N_{\mathrm{fr}}$** (Fused Rings): Count of rings sharing atoms or bonds.
* **$N_{\mathrm{ta}}$**: Total number of atoms
* **$N_{\mathrm{mr}}$**: total number of macrocycles
* **$W_{m}$**: Weight for macrocycle descriptors.
* **$W_{i}$**: Weight for topological descriptors.
* **$D_{i}$**: Topological ring diversity descriptor.


## Ring Complexity Index
$RCI=\frac{TRS}{nRingAtoms}$  
where TRS is the total ring size and $nRingAtoms$ is the number of atoms belonging to a ring.
Ref: Gasteiger, J., & Jochum, C. (1979). An Algorithm for the Perception of Synthetically Important Rings. Journal of Chemical Information and Computer Sciences, 19(1), 43–48. https://doi.org/10.1021/ci60017a011  


## Requirements
```python
Python==3.13.2
rdkit==2025.03.2
scipy==1.15.1
```

## QRCI Calculation

```python
from QRCI.QRCI import QRCICalculator, get_QRCIproperties
from QRCI.RCI import RCICalculator

qrci_calc = QRCICalculator(weights='mean')
score_mean = qrci_calc('C1=CCOCc2cc(ccc2OCCN2CCCC2)Nc2nccc(n2)-c2cccc(c2)COC1')
print(f"QRCI(default/mean weights): {score_mean:.4f}")
#QRCI(default/mean weights): 4.0330

***************************************************************************************
mol = Chem.MolFromSmiles('C1=CCOCc2cc(ccc2OCCN2CCCC2)Nc2nccc(n2)-c2cccc(c2)COC1')
props = get_qrci_properties(mol)
print(props)
#QRCIproperties(nAromHetero=1, nAromCarbo=2, nAliHetero=2, nAliCarbo=0, nSatHetero=1, nSatCarbo=0, nMacrocycles=1, TRS=41, nRingAtom=32, nFusedRing=4, SF=1.0857142857142856)

```

## Ring Descriptors Calculation

```python
from QRCI.ring_descriptors import (
    get_num_stereocenters,
    get_num_macrocycles,
    calculate_number_of_heteroatoms,
    count_ring_atoms,
    calculate_heteroatom_ratio,
    calculate_nIR,
    calculate_nFR,
    calculate_TRS,
    calculate_Rperim,
    calculate_nrs,
    calculate_cyclomatic_number,
    calculate_nnrs,
    calculate_mcd,
    calculate_ring_fusion_density,
    Calc_ARR,
    Calc_Ar_Alk_balance,
    calculate_heterorings_ratio,
)

#calculate ring descriptors
ring_descriptors = {
    "num_stereocenters": get_num_stereocenters(mol),
    "num_macrocycles": get_num_macrocycles(mol),
    "num_heteroatoms": calculate_number_of_heteroatoms(mol),
    "num_ring_atoms": count_ring_atoms(mol),
    "heteroatom_ratio": calculate_heteroatom_ratio(mol),
    "nIR": calculate_nIR(mol),
    "nFR": calculate_nFR(mol),
    "TRS": calculate_TRS(mol),
    "Rperim": calculate_Rperim(mol),
    "nRS": calculate_nrs(mol),
    "cyclomatic_number": calculate_cyclomatic_number(mol),
    "nNRS": calculate_nnrs(mol),
    "mcd": calculate_mcd(mol),
    "ring_fusion_density": calculate_ring_fusion_density(mol),
    "ARR": Calc_ARR(mol),
    "Ar_Alk_balance": Calc_Ar_Alk_balance(mol),
    "heterorings_ratio": calculate_heterorings_ratio(mol),
}

for k, v in ring_descriptors.items():
    print(f"{k}: {v}")
#num_stereocenters: 0
#num_macrocycles: 1
#num_heteroatoms: 7
#num_ring_atoms: 32
#heteroatom_ratio: 0.2
#nIR: 1
#nFR: 4
#TRS: 41
#Rperim: 41
#nRS: 2
#cyclomatic_number: 5
#nNRS: 0.4
#mcd: 0.9142857142857143
#ring_fusion_density: 0.2
#ARR: 0.4615
#Ar_Alk_balance: 6
#heterorings_ratio: 0.6

```


## License
Code is released under MIT LICENSE.


## Cite

* Gasteiger, J. and Jochum, C., 1979. An algorithm for the perception of synthetically important rings. Journal of Chemical Information and Computer Sciences, 19(1), pp.43-48.
* Ertl, P., Schuffenhauer, A. Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions. J Cheminform 1, 8 (2009). https://doi.org/10.1186/1758-2946-1-8
* Krzyzanowski, A., Pahl, A., Grigalunas, M., & Waldmann, H. (2023). Spacial Score─A Comprehensive Topological Indicator for Small-Molecule Complexity. Journal of medicinal chemistry, 66(18), 12739–12750. https://doi.org/10.1021/acs.jmedchem.3c00689
* Wang J, Xu K, Ma T, Zhang X, Ma P, Li  C, et al. A Quantitative Ring Complexity Index for Profiling Ring Topology and Chemical Diversity. ChemRxiv. 2025; doi:[10.26434/chemrxiv-2025-mlqwl-v2](https://doi.org/10.26434/chemrxiv-2025-mlqwl-v2)  This content is a preprint and has not been peer-reviewed.





