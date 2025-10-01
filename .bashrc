# ~/.bashrc for GitHub Codespace
# Visa git-information i prompten
parse_git_info() {
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
  status=$(git status --porcelain 2>/dev/null)
  dirty=""
  if [ -n "$status" ]; then dirty="*"; fi
  echo "($branch$dirty)"
}
export PS1='\u@\h:\w$(parse_git_info)\\$ '