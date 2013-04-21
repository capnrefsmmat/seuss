<?php
$defaultScheme = "aabba";
$defaultBrains = "bbbjj";
$defaultLen = 7;
$defaultLines = 2;

$brainChoices = array('b', 'e', 'c', 'w', 'u', 'j', 'l', 'k', 't', 'k', 
                      'x', 's', 'n', 'f');
if (isset($_POST['rhymescheme']) && isset($_POST['brains']) && isset($_POST['linelen'])
    && isset($_POST['numlines']))
{
    foreach(str_split($_POST['brains']) as $brain)
    {
        if (array_search($brain, $brainChoices, true) === false)
        {
            die("pick a real brain, buster");
        }
    }
    if (!ctype_alnum($_POST['rhymescheme']))
    {
        die("pick a real rhymescheme, buster");
    }
    if (!ctype_digit($_POST['linelen']) || !ctype_digit($_POST['numlines']))
    {
        die('pick real numbers, buster');
    }

    if ($_POST['numlines'] > 5)
    {
        die('dude, do you want to kill my server or something? use less poems!');
    }

    $output = shell_exec("./rhyme.py " . escapeshellcmd($_POST['brains'] . " " . $_POST['rhymescheme'] . " " . $_POST['linelen'] . " " . $_POST['numlines']));
    
    $poem = nl2br(htmlentities($output));
    
    $defaultScheme = htmlentities($_POST['rhymescheme']);
    $defaultBrains = htmlentities($_POST['brains']);
    $defaultLen = htmlentities($_POST['linelen']);
    $defaultLines = htmlentities($_POST['numlines']);
}


?>
<html>
    <head>
        <title>Poetry Generator of Doooom</title>
        <style type="text/css">
        p
        {
            font-family: verdana, helvetica, sans-serif;
        }
        </style>
    </head>
    <body>
        <h1>Carnac the Magnificent Poetry Generator</h1>
        <h3>Your Poem</h3>
        <?php if (isset($poem)) { ?>
        <p>
            <?php echo $poem; ?>
        </p>
        <?php } ?>
        <div style="float:right">
            <h3>Sources</h3>
            <ul>
                <li>b: Bible</li>
                <li>w: Weeping Cock</li>
                <li>e: Erotica</li>
                <li>n: Henri Bergson</li>
                <li>f: Fanny Hill</li>
                <li>j: James Joyce</li>
                <li>t: Mark Twain</li>
                <li>x: Wikipedia on sex</li>
                <li>k: Franz Kafka</li>
                <li>s: Kamasutra</li>
                <li>c: Lewis Carroll</li>
                <li>l: Legalese</li>
                <li>u: Unabomber manifesto</li>
            </ul>
        </div>
        <h3>Make a Poem</h3>
        <form method="post" action="poetry.php">
            Rhymescheme: <input type="text" name="rhymescheme" value="<?php echo $defaultScheme ?>" /> <br/>
            Brains: <input type="text" name="brains" value="<?php echo $defaultBrains ?>" /> <br/>
            Line length (in words): <input type="text" name="linelen" value="<?php echo $defaultLen ?>" /><br/>
            Number of poems: <input type="text" name="numlines" value="<?php echo $defaultLines ?>" /><br/>
            <input type="submit" value="Poetify!" />
        </form>
    </body>
</html>
