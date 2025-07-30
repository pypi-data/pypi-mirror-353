
## Available Scripts

* extract_pyinv_examples (in crtomo_tests)
* pycrtomo_test (in crtomo_tests)
* CRMod (in crtomo_wrappers)
* CRTomo (in crtomo_wrappers)
* CutMcK (in crtomo_wrappers)

## Updating CRMod

    ./gen_pycrmod.sh
    cp -r output_pycrmod both_v1/pycrmod_vX
    # in meson.build:
        * remove virtualenv-specific python path
        * remove project(...) call, as we use this project as a subproject
