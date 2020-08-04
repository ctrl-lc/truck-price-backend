$dir = "C:\Users\a.leshchenko\documents\CTRL\Stocks"
$datacol_dir = '"C:\Program Files\Datacol7\datacol7.exe"'
$campaign_dir = "C:\Users\a.leshchenko\AppData\Roaming\Datacol7\Campaigns\leshchenko\trucks - parsing"
$temp = $dir + "\temp\1.csv"
    
    
$BIGML_USERNAME = "leshchenko"
$BIGML_API_KEY = "724c06d2530db8744a01ea24cdce30911cdba42d"

function Stage-0 {

<#
(Get-Date).toString() + ": Upgrading python packages..."

& pip3.exe install bigmler --upgrade
& pip3.exe install gspread --upgrade

(Get-Date).toString() + ": Packages upgraded."
#>
}

function Stage-1 {
    (Get-Date).toString() + ": ---------- Parsing listings - Stage 1..."

    $col_files = @( 
        $campaign_dir + "\auto.ru - тягачи - без карточек.par";
        $campaign_dir + "\auto.ru - полуприцепы - без карточек.par";  
<#        $campaign_dir + "\drom.ru - тягачи.par"  #>
    )

    foreach ($f in $col_files) { 
        (Get-Date).toString() + ": Processing " + $f + " ..."
        $arg = 'config="' + $f + '" autolaunch'
        Start-Process -FilePath $datacol_dir -ArgumentList $arg -Wait -NoNewWindow
    }
    
    (Get-Date).toString() + ": Starting Tableau Prep - Preparing Data for valuation..."
    
    $flowfile = $dir+"\scripts\stage-1.tfl"
    & tableau-prep-cli.bat -t "$flowfile"
    
    (Get-Date).toString() + ": Stage 1 complete."
    
        
}


function Stage-2 {
    (Get-Date).toString() + ": ---------- Starting predictions - Stage 2..."

    $predictions =
        @{ 
            inputfile = $dir+"\data\Тягачи для проценки.csv";
            command = "deepnet --deepnet deepnet/5e8cb9e1c5f953216a07d9f7";
            outputfile = $dir+"\data\trucks - evaluated.csv"
         },
    
         @{ 
            inputfile = $dir+"\data\Прицепы для проценки.csv";
            command = "--ensemble ensemble/5e8c5d40440ca118060bcde3";
            outputfile = $dir+"\data\trailers - evaluated.csv"
         }
         
    foreach ($p in $predictions) {
        (Get-Date).toString() + ": Processing " + $p.inputfile + " ..."
    
        (Get-Date).toString() + ": Length: " + (Get-Content -Path $p.inputfile).length
    
        $text = (Get-Content -Path $p.inputfile -ReadCount 0) -join "`n"
        $text -replace ';', ',' | Set-Content -Path $temp -Encoding UTF8
        
        (Get-Date).toString() + ": Starting bigmler..."
    
        $arg = $p.command + ' --test "' + $temp + '" --output "' + $p.outputfile +
             '" --username ' + $BIGML_USERNAME + ' --api-key ' + $BIGML_API_KEY + 
             ' --prediction-info full --prediction-header --remote --locale "en_US.UTF-8"' +
             ' --test-separator ";"'
        
        Start-Process "bigmler.exe" -ArgumentList $arg -Wait -NoNewWindow
    
        Remove-Item $temp
    
    }


    (Get-Date).toString() + ": Starting Tableau Prep - Preparing tasks for comment parsing..."

    $flowfile = $dir+"\scripts\stage-2.tfl"
    & tableau-prep-cli.bat -t "$flowfile"
    $test = $dir + "\data\comments task - whole.csv"

    (Get-Date).toString() + ": Length: " + (Get-Content -Path $test).length


    (Get-Date).toString() + ": Stage 2 complete."
    
        
}

function Stage-3 {
    (Get-Date).toString() + ": --------- Starting comment processing - Stage 3..."

    $col_files = @(
        $campaign_dir + '\auto.ru - комментарии.par' <#; 
        $campaign_dir + '\drom.ru - comments.par' #>
    )
   
    foreach ($p in $col_files) { 
        (Get-Date).toString() + ": Processing " + $p + " ..."
    
        (Get-Date).toString() + ": Collecting data from the web..."
        $arg = 'config="' + $p + '" autolaunch'
        Start-Process -FilePath $datacol_dir -ArgumentList $arg -Wait

    }

<#    (Get-Date).toString() + ": Collecting comments from drom.ru..."
    & python.exe $dir"\scripts\drom_comments.py"
#>
    
    (Get-Date).toString() + ": Starting Tableau Prep - Preparing Data for valuation..."
    
    $flowfile = $dir+"\scripts\stage-3.tfl"
    & tableau-prep-cli.bat -t "$flowfile"

    (Get-Date).toString() + ": Converting..."

    $input = $dir + "\data\comments - prepared.csv"
    $text = (Get-Content -Path $input -ReadCount 0) -join "`n"
    $text -replace ';', ',' | Set-Content -Path $temp -Encoding UTF8
    (Get-Date).toString() + ": Length: " + (Get-Content -Path $temp).length

    (Get-Date).toString() + ": Starting bigmler..."

    $command = "--ensemble ensemble/5e909ebbc5f953216a084693" 
    $output = $dir + "\data\comments evaluated.csv"

    $arg = $command + ' --test "' + $temp + '" --output "' + $output +
    '" --username ' + $BIGML_USERNAME + ' --api-key ' + $BIGML_API_KEY +
    ' --prediction-info full --prediction-header --remote --locale "en_US.UTF-8"'

    Start-Process "bigmler.exe" -ArgumentList $arg -Wait -NoNewWindow

    (Get-Date).toString() + ": Length: " + (Get-Content -Path $output).length

    Remove-Item $temp

    (Get-Date).toString() + ": Data collection Stage 3 complete."
}

function Stage-4 {
    (Get-Date).toString() + ": ------------- Downloading verifications - Stage 4..." 
    
    & python.exe $dir"\scripts\download_ads.py"

    (Get-Date).toString() + ": Updating regions file..."

    & python.exe $dir"\scripts\update_regions.py"

    (Get-Date).toString() + " Starting Tableau Prep to prepare final data..."

    $flowfile = $dir+"\scripts\stage-4.tfl"
    & tableau-prep-cli.bat -t "$flowfile"
    
    (Get-Date).toString() + ": Records in the final data file: " + (Get-Content -Path $dir"\data\full_stock.csv").length
    
    if (Test-Path $dir"\data\archive.csv") {
    
        (Get-Date).toString() + ": Backing up the archive..."
    
        Copy-Item $dir"\data\archive.xlsx" -Destination $dir"\data\archive.xlsx.bak"
        
        (Get-Date).toString() + ": Archive backed up."
        
        Remove-Item $dir"\data\archive.xlsx"
    
        $arg = "-nme -oice """+$dir+"\data\archive.csv"" """+$dir+"\data\archive.xlsx"""
        Start-Process -FilePath "C:\Program Files\Microsoft Office\Office16\excelcnv.exe" -ArgumentList $arg -Wait -NoNewWindow
    
        if (Test-Path $dir"\data\archive.xlsx") {
            Remove-Item $dir"\data\archive.csv"
            (Get-Date).toString() + ": Archive updated with today's data."
        } else {
            (Get-Date).toString() + ": Error converting CSV to XLS"
            (Get-Date).toString() + ": Restoring backup archive"
            Copy-Item $dir"\data\archive.xlsx.bak" -Destination $dir"\data\archive.xlsx"
            Exit
        }
    
    } else {
        (Get-Date).toString() + ": New archive file (archive.csv) hasn't been found. Check Tableau Prep script."
        Exit
    }                                                                    
    
    (Get-Date).toString() + ": Uploading ads to Google Sheets..."
    
    & python.exe $dir"\scripts\upload_stock.py"

    (Get-Date).toString() + ": Uploading verification data to Google Firestore..."

    & python.exe $dir"\scripts\upload_verification.py"    
    
}

<#
Stage-0
" "
Stage-1
" "#>
Stage-2
" "
Stage-3
" "
Stage-4
" "
(Get-Date).toString() + ": All done. Kudos to Alexey Leshchenko!"
