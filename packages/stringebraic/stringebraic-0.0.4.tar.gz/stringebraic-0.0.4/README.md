  <figure>
    <img src="https://github.com/kwyip/stringebraic/blob/main/logo.png?raw=True" alt="logo" height="143" />
    <!-- <figcaption>An elephant at sunset</figcaption> -->
  </figure>

[![](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/kwyip/stringebraic/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stringebraic)](https://pypi.org/project/stringebraic/)
[![Static Badge](https://img.shields.io/badge/CalVer-2025.0416-ff5733)](https://pypi.org/project/stringebraic)
[![Static Badge](https://img.shields.io/badge/PyPI-wheels-d8d805)](https://pypi.org/project/stringebraic/#files)
[![](https://pepy.tech/badge/stringebraic/month)](https://pepy.tech/project/stringebraic)

[stringebraic](https://stringebraic.github.io/)
===============================================

love manually cleaning up messy `.bib` files? `stringebraic.py` heroically steps in to remove those lazy, _unused_ citations and _reorder_ the survivors exactly as they appear in the `.tex` file—because, clearly, chaos is the default setting for bibliographies.

In layman's terms, it automates Pauli algebra management by:

1.  removing unused citations,
2.  reordering the remaining ones to match their order of appearance in the `.tex` file.

**Input Files:**

*   `input_string_list.pkl` – The LaTeX source file.
*   `input_string_coeff_list.pkl` – The original Pauli algebra file.
*   `pauli_matrix_list.pkl` – The original Pauli algebra file.
*   `pauli_coeff_list.pkl` – The original Pauli algebra file.

These input files will **remain unchanged**.

**Output:**

*   `The inner product value` – A scalar for what the inner product (e.g., expected energy) is.

* * *

Installation
------------

It can be installed with `pip`, ideally by using a [virtual environment](https://realpython.com/what-is-pip/#using-pip-in-a-python-virtual-environment). Open up a terminal and install the package and the dependencies with:  
  

    `pip install stringebraic`

_or_

    `python -m pip install stringebraic`

  
_🐍 This requires Python 3.8 or newer versions_

* * *

### Steps to Clean Your Pauli algebra

1.  **Prepare the input files (e.g., by downloading them from Overleaf)**.
2.  **Run the command to generate a new `.bib` file (for example, you may name it `ref_opt.bib`)**:  
      
    
           `bibopt main.tex ref.bib ref_opt.bib`
    
      
    
3.  **Use the Cleaned Pauli Algebra**  
    Replace `ref.bib` with `ref_opt.bib` in your LaTeX project.

* * *

### Test

You may test the installation using the sample input files (`sample_main.tex` and `sample_ref.bib`) located in the test folder.

---

♥ Lastly executed on Python `3.10` on 2025-04-16.