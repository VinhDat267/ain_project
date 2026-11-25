# Let Microsoft Word update the table of contents and caption numbers, save the .docx,
# export a PDF preview and print the page on which every Heading 1 starts.
# Usage: powershell -ExecutionPolicy Bypass -File report\finalize_report.ps1 report\P12_report_DRAFT.docx
param(
    [Parameter(Mandatory = $true)][string]$DocxPath,
    [string]$PdfPath = ""
)
$ErrorActionPreference = "Stop"
$full = (Resolve-Path $DocxPath).Path
if (-not $PdfPath) { $PdfPath = [System.IO.Path]::ChangeExtension($full, ".preview.pdf") }
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($full, $false, $false)
    $null = $doc.Fields.Update()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $null = $doc.Fields.Update()
    $doc.Save()
    $doc.ExportAsFixedFormat($PdfPath, 17)
    "PDF: $PdfPath"
    "Total pages: " + $doc.ComputeStatistics(2)
    foreach ($p in $doc.Paragraphs) {
        $style = $p.Style.NameLocal
        if ($style -eq "Heading 1" -or $style -eq "Front Heading") {
            # 1 = page number inside the section (what the footer shows), 3 = physical page.
            "{0,4} {1,4}  {2}" -f $p.Range.Information(1), $p.Range.Information(3), $p.Range.Text.Trim()
        }
    }
    $doc.Close()
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
