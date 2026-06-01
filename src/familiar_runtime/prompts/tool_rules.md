    (tools
      (tool :id read_file :sig "read_file(path, offset?, limit?)"
        :note "Always call before edit_file. Returns file with line numbers.")
      (tool :id write_file :sig "write_file(path, content)"
        :note "Write a complete file. Prefer edit_file for small changes.")
      (tool :id edit_file :sig "edit_file(path, old_string, new_string)"
        :note "Exact string patch. old_string must be unique in file.")
      (tool :id multi_edit_file :sig "multi_edit_file(path, edits[])"
        :note "Atomic multiple exact string replacements in one file.")
      (tool :id glob      :sig "glob(pattern, path?)"
        :note "Find files by glob pattern e.g. **/*.py")
      (tool :id grep      :sig "grep(pattern, path?, glob?, output_mode?)"
        :note "Search file contents by regex.")
      (tool :id git_status :sig "git_status()"
        :note "Show concise working tree state.")
      (tool :id git_diff :sig "git_diff(path?)"
        :note "Show working tree diff.")
      (tool :id git_apply_patch :sig "git_apply_patch(patch)"
        :note "Apply a unified diff patch.")
      (tool :id run_tests :sig "run_tests(command?, timeout?)"
        :note "Run tests. Only available when CODING_BASH=true.")
      (tool :id bash      :sig "bash(command, timeout?)"
        :note "Shell command. Only available when CODING_BASH=true."))
