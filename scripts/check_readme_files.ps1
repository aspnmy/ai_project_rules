#!/usr/bin/env pwsh

# 递归检查README文件的脚本
$baseDir = "u:/git/binwalk/.trae/rules"
$results = @()

function Check-ReadmeInDir($dirPath) {
    Write-Output "检查目录: $dirPath"
    
    # 检查README.md是否存在
    $readmeExists = Test-Path "$dirPath\README.md"
    
    # 检查README_En.md是否存在（根据规范，如果有PG_ProjectUpLang设置为En）
    $readmeEnExists = Test-Path "$dirPath\README_En.md"
    
    # 将结果添加到数组
    $results += [PSCustomObject]@{
        Directory = $dirPath
        README_MD_Exists = $readmeExists
        README_EN_MD_Exists = $readmeEnExists
        Is_Compliant = $readmeExists  # 当前根据规范，README.md是必须的，README_En.md可能是可选的
    }
    
    # 递归检查子目录
    Get-ChildItem -Path $dirPath -Directory | ForEach-Object {
        Check-ReadmeInDir $_.FullName
    }
}

# 开始检查
Check-ReadmeInDir $baseDir

# 输出结果
Write-Output "\n===== README文件检查报告 ====="
$results | Format-Table -AutoSize Directory, README_MD_Exists, README_EN_MD_Exists, Is_Compliant

# 统计不合规的目录
$nonCompliant = $results | Where-Object { -not $_.Is_Compliant }
Write-Output "\n不合规的目录数量: $($nonCompliant.Count)"
if ($nonCompliant.Count -gt 0) {
    Write-Output "\n不合规的目录列表:"
    $nonCompliant | ForEach-Object { Write-Output $_.Directory }
}

# 将结果保存到文件
$results | Export-Csv -Path "$baseDir\readme_check_report.csv" -NoTypeInformation
Write-Output "\n报告已保存到: $baseDir\readme_check_report.csv"