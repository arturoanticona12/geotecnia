# Compila el manuscrito y el suplemento de HiBER con la clase oficial ascelike-new (MiKTeX).
# Los .tex se regeneran con ..\build_hiber_asce6.py y ..\build_hiber_suplemento6.py; no editarlos a mano.
# Uso (desde esta carpeta):  .\compilar.ps1
$ErrorActionPreference = "Stop"
$env:Path = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;" + $env:Path
Set-Location $PSScriptRoot
pdflatex -interaction=nonstopmode HiBER_IJGM_manuscript_r6.tex | Out-Null
bibtex HiBER_IJGM_manuscript_r6 | Out-Null
pdflatex -interaction=nonstopmode HiBER_IJGM_manuscript_r6.tex | Out-Null
pdflatex -interaction=nonstopmode HiBER_IJGM_manuscript_r6.tex | Out-Null
pdflatex -interaction=nonstopmode HiBER_IJGM_supplement_r6.tex | Out-Null
pdflatex -interaction=nonstopmode HiBER_IJGM_supplement_r6.tex | Out-Null
foreach ($n in "HiBER_IJGM_manuscript_r6", "HiBER_IJGM_supplement_r6") {
    $log = Get-Content "$n.log" -Encoding utf8
    $pag = ($log | Select-String "Output written").Line
    $mal = ($log | Select-String "^! |Overfull|Missing character|Citation .* undefined").Count
    "{0}: {1} | problemas: {2}" -f $n, $pag, $mal
}
