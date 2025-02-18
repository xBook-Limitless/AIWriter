# 删除缓存和构建文件
Get-ChildItem -Path . -Include __pycache__, .mypy_cache, .pytest_cache -Recurse | Remove-Item -Recurse -Force
Remove-Item -Path .\*.log, .\*.tmp -Force 