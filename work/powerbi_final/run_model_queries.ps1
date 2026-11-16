param([Parameter(Mandatory=$true)][int]$Port,[string]$OutputName='model_query_results.json')
$ErrorActionPreference='Stop'
$lib='C:\Program Files (x86)\Microsoft SQL Server Management Studio 20\Common7\IDE'
Add-Type -Path (Join-Path $lib 'Microsoft.AnalysisServices.AdomdClient.dll')
$connection=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port")
$connection.Open()
$results=New-Object System.Collections.Generic.List[object]
try{
 $queries=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'model_test_queries.json') -Raw -Encoding UTF8 | ConvertFrom-Json
 foreach($q in $queries){
  try{
   $command=$connection.CreateCommand()
   $command.CommandText=$q.query
   $command.CommandTimeout=180
   $reader=$command.ExecuteReader()
   $rows=New-Object System.Collections.Generic.List[object]
   try{
    while($reader.Read()){
     $row=[ordered]@{}
     for($i=0;$i -lt $reader.FieldCount;$i++){
      $v=$reader.GetValue($i)
      $row[$reader.GetName($i)]=if($v -is [DBNull]){$null}else{$v}
     }
     $rows.Add($row)
    }
   }finally{$reader.Close()}
   $results.Add([ordered]@{name=$q.name;rows=@($rows.ToArray());error=$null})
   Write-Output ($q.name+' rows='+$rows.Count)
  }catch{
   $results.Add([ordered]@{name=$q.name;rows=@();error=$_.Exception.Message})
   Write-Output ($q.name+' ERROR '+$_.Exception.Message)
  }
 }
}finally{$connection.Close()}
$outputPath=Join-Path $PSScriptRoot $OutputName
ConvertTo-Json -InputObject @($results.ToArray()) -Depth 20 | Set-Content -LiteralPath $outputPath -Encoding UTF8
Write-Output ('Saved '+$results.Count+' query results')
