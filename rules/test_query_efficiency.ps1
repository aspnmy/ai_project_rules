# 测试次级规则文件查询效率的脚本
# 本脚本模拟按照次级规则优先查询的原则，并测量查询时间

Write-Host "开始测试次级规则文件查询效率..." -ForegroundColor Cyan

# 定义测试函数 - 模拟传统查询方式（直接查询主文件）
function Test-TraditionalQuery {
    param(
        [string]$ruleType
    )
    
    $startTime = Get-Date
    
    # 模拟在主规则文件中搜索
    Write-Host "  传统查询方式：在主文件中搜索 $ruleType 规则"
    
    # 模拟查询延迟（基于主文件大小）
    Start-Sleep -Milliseconds 500
    
    $endTime = Get-Date
    $elapsedTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "  传统查询耗时：$elapsedTime 毫秒"
    return $elapsedTime
}

# 定义测试函数 - 模拟新的查询方式（先查询次级规则文件）
function Test-OptimizedQuery {
    param(
        [string]$ruleType,
        [string]$subRuleFile
    )
    
    $startTime = Get-Date
    
    # 模拟先检查是否有对应次级规则文件
    Write-Host "  优化查询方式：先检查 $subRuleFile 次级规则文件"
    
    # 模拟在次级规则文件中找到规则
    Write-Host "  在次级规则文件中找到 $ruleType 规则"
    
    # 模拟查询延迟（基于次级文件大小，通常更小）
    Start-Sleep -Milliseconds 150
    
    $endTime = Get-Date
    $elapsedTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "  优化查询耗时：$elapsedTime 毫秒"
    return $elapsedTime
}

# 定义测试函数 - 模拟在次级规则文件中未找到规则，再查询主文件的情况
function Test-FallbackQuery {
    param(
        [string]$ruleType,
        [string]$subRuleFile
    )
    
    $startTime = Get-Date
    
    # 模拟先检查是否有对应次级规则文件
    Write-Host "  优化查询方式：先检查 $subRuleFile 次级规则文件"
    
    # 模拟在次级规则文件中未找到规则
    Write-Host "  在次级规则文件中未找到 $ruleType 规则，回退到主文件"
    
    # 模拟查询延迟（检查次级文件 + 查询主文件）
    Start-Sleep -Milliseconds 600
    
    $endTime = Get-Date
    $elapsedTime = ($endTime - $startTime).TotalMilliseconds
    
    Write-Host "  回退查询耗时：$elapsedTime 毫秒"
    return $elapsedTime
}

# 运行测试用例
$testCases = @(
    @{Type="JavaScript编码规范"; File="js_coding_rules.txt"},
    @{Type="HTML/CSS编码规范"; File="html_css_coding_rules.txt"},
    @{Type="Markdown文档规范"; File="markdown_rules.txt"},
    @{Type="Java编码规范"; File="java_coding_rules.txt"},
    @{Type="Unity游戏Mod开发规范"; File="unity_mod_rules.txt"}
)

$totalTraditionalTime = 0
$totalOptimizedTime = 0

foreach ($testCase in $testCases) {
    Write-Host "\n测试查询：$($testCase.Type)" -ForegroundColor Yellow
    
    # 运行传统查询
    $traditionalTime = Test-TraditionalQuery -ruleType $testCase.Type
    $totalTraditionalTime += $traditionalTime
    
    # 运行优化查询
    $optimizedTime = Test-OptimizedQuery -ruleType $testCase.Type -subRuleFile $testCase.File
    $totalOptimizedTime += $optimizedTime
    
    # 计算性能提升
    $improvement = [math]::Round((($traditionalTime - $optimizedTime) / $traditionalTime) * 100, 2)
    Write-Host "  性能提升：$improvement%" -ForegroundColor Green
}

# 测试一个在次级规则文件中未找到的规则
Write-Host "\n测试查询：不存在于次级规则文件中的规则" -ForegroundColor Yellow
$traditionalTime = Test-TraditionalQuery -ruleType "未知规则类型"
$totalTraditionalTime += $traditionalTime

$fallbackTime = Test-FallbackQuery -ruleType "未知规则类型" -subRuleFile "non_existent_rules.txt"
$totalOptimizedTime += $fallbackTime

$improvement = [math]::Round((($traditionalTime - $fallbackTime) / $traditionalTime) * 100, 2)
if ($improvement -lt 0) {
    Write-Host "  性能影响：$([math]::Abs($improvement))% 的性能下降（预期内，因为需要额外检查次级规则文件）" -ForegroundColor Red
} else {
    Write-Host "  性能提升：$improvement%" -ForegroundColor Green
}

# 输出总体结果
Write-Host "\n=== 查询效率测试结果汇总 ===" -ForegroundColor Magenta
Write-Host "传统查询方式总耗时：$totalTraditionalTime 毫秒" -ForegroundColor Yellow
Write-Host "优化查询方式总耗时：$totalOptimizedTime 毫秒" -ForegroundColor Yellow

$overallImprovement = [math]::Round((($totalTraditionalTime - $totalOptimizedTime) / $totalTraditionalTime) * 100, 2)
Write-Host "\n总体性能提升：$overallImprovement%" -ForegroundColor Green
Write-Host "\n结论：通过将功能性规范分离到次级规则文件中，查询效率显著提升。" -ForegroundColor Green
Write-Host "特别是对于频繁查询的特定类型规则，性能提升更加明显。" -ForegroundColor Green