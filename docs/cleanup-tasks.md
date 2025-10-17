 # Cleanup Tasks (Step-by-Step)
 
 ## 1. Branch and scaffold
 - [ ] Create branch: `git switch -c chore/cleanup-refactor` and push with `git push -u origin chore/cleanup-refactor`
 - [ ] Commit this plan and tasks markdown
 
 ## 2. Safe deletions (no code change risk)
 - [ ] Remove `src/flowerpower/_settings.py`
 - [ ] Remove `src/flowerpower/settings/_backend.py`
 - [ ] Remove empty dir `src/flowerpower/plugins/mqtt/`
 - [ ] Remove empty dir `src/flowerpower/plugins/io/helpers/`
 - [ ] Remove `src/flowerpower/utils/monkey.py`
 
 ## 3. Safe bug fixes
 - [ ] Fix `pipeline/pipeline.py` executor branching and duplicate imports
 - [ ] Fix `pipeline/io.py` `_print_export_success` recursion
 
 ## 4. Hygiene
 - [ ] Remove unused/duplicate imports (ruff --fix)
 - [ ] Ensure no behavior changes in logs/prints
 
 ## 5. Validation
 - [ ] Run tests: `pytest -q`
 - [ ] Run typecheck: `mypy`
 - [ ] Run lint: `ruff .`
 
 ## 6. PR
 - [ ] `gh pr create --fill` (or `--draft`) and request review
 
