<?php 
    $document_id = $_GET['did'];

    $db = new mysqli("eltanin.cis.cornell.edu", "annotator", "Ann0tateTh!s", "FrameAnnotation");
    if($db->connect_errno > 0) {
        die('Unable to connect to database [' . $db->connect_error . ']');
    }
    $db->set_charset('ISO-8859-1');
    $q = "SELECT doc_html FROM Documents WHERE doc_id =". $document_id;

    if ($result = $db->query($q)) {

        /* fetch associative array */
        while ($row = $result->fetch_assoc()) {
            //$row = $q->fetch_row();
            $passage = $row['doc_html'];
        }

        $result->free();
    } else {
        die('There was an error running the query [' . $db->error . ']');
    }





    header('Content-Type: text/html; charset=ISO-8859-1');
    #$passage = "<h1> Disparities in Americans' Health on the Rise; Income, Race, Insurance Major Factors in Differences </h1><p> Even as health care costs continue to escalate, many Americans- especially minorities and the poor- still do not receive high-quality care, according to federal reports published by the National Institutes of Health. The quality of health care is improving slowly and some racial disparities are narrowing, the reports found, but gaps persist and Hispanics appear to be falling even further behind. Officials called the reports, mandated by Congress to study the quality and distribution of health care, the most comprehensive assessments of their kind. </p><p> \"We can do better,\" Former Health and Human Services Secretary Mike Leavitt said at a Washington conference on racial and ethnic disparities in health care. \"Disparities and inequities still exist. Outcomes vary. Treatments are not received equally.\" </p><p> One study of 13,000 New Jersey heart patients found that far fewer African American patients received catheterization to clear the arteries, despite exhibiting the same symptoms. Another study involving 13,600 nursing home residents found that blacks \"had a 63 percent greater probability of being untreated for pain relative to whites.\" </p><p> In the National Healthcare Disparities Report, researchers found more measures on which the quality gap between whites and racial minorities was shrinking than widening. But the report found that major disparities remained for all groups and that the gap had widened for Hispanics. </p><p> Forty-six disparities were discussed in the report. Of those experienced by blacks, 58 percent were narrowing and 42 percent were widening, the researchers found. For Hispanics, 41 percent of disparities were narrowing, whereas 59 percent were becoming larger. </p><p> Embedded in the American urban landscape, you'd see poor, black people inhaling lethal amounts of exhaust and nicotine. Their hearts would be heavy with fat and arteryclogging plaque, while their brains would be awash in alcohol and drugs. Some might see such a condition as terminal, set up a triage and hope it works itself out. But a good doctor might recognize the regenerative powers of the body politic and come up with a comprehensive treatment plan that also attacks root causes- including the twin cancers of racism and poverty. </p><p> Take, for example, that the average life span for black men in the nation's capital is about 57 years, a year more than that of Native Americans on the Pine Ridge Reservation in South Dakota but about 23 years lower than that of white men in the District. That kind of racial and economic disparity in wellbeing reflects fundamental problems in America's health care and health insurance systems. There is doubt that all reform proposals under consideration in Congress will fully correct these inequalities. But one thing is certain: The current health care system does much to perpetuate them.</p>";
    $words = explode(" ", $passage);

?>


<html>
<head>
    <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
    <script src="http://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
    <script type = "text/javascript" src="main.js"></script>
    <script src="scripts/jquery-1.9.1.js"></script>
    <script src="scripts/jquery-ui-1.10.3.custom.js"></script>
    <link href="css/reset.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">
    <link href="css/smoothness/jquery-ui-1.10.3.custom.css" rel="stylesheet">
    <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
</head>

<body>
    <div id="passage">

        <?php for ($i = 0; $i < count($words); $i++) { 
            // word</h1><p>word case
            if (is_numeric(strpos($words[$i], "><"))) {
                $str_w_tag = explode("><", $words[$i]);
                $left = explode("<", $str_w_tag[0]);
                $right = explode(">", $str_w_tag[1]);
                $str = $left[0];
                print "<span id=s-" . $i . " class=\"space\">&nbsp;</span><span id = " . $i . " class=\"passage_words\">" . $str . "</span>";
               
                print "<".$left[1].">"."<".$right[0].">";  
                
                $i++;
                array_splice($words, $i, 0, $right[1]);
                $str = $words[$i];
                //var_dump($words);
                print "<span id=s-" . $i . " class=\"space\">&nbsp;</span><span id = " . $i . " class=\"passage_words\">" . $str . "</span>";

            } else if (is_numeric(strpos($words[$i], "<"))) {
            //first word or last word
                $str_w_tag = explode("<", $words[$i]);
                if ($str_w_tag[0] == '') { 
                    $sep = explode(">", $str_w_tag[1]);
                    print "<".$sep[0].">";
                    $str = $sep[1];
                    print "<span id=s-" . $i . " class=\"space\">&nbsp;</span><span id = " . $i . " class=\"passage_words\">" . $str . "</span>";
                } else {
                    $str = $str_w_tag[0];
                    print "<span id=s-" . $i . " class=\"space\">&nbsp;</span><span id = " . $i . " class=\"passage_words\">" . $str . "</span>";
                    print "<".$str_w_tag[1];
                }  
                
                //echo "i: " . $i . "str: " . $str;
            } else {
                $str = $words[$i];
                print "<span id=s-" . $i . " class=\"space\">&nbsp;</span><span id = " . $i . " class=\"passage_words\">" . $str . "</span>";
            }

            
        } 
        ?>
    </div>
    <div id="annotated">
        <h1> Currently Selected Text </h1>
        <table id="annotationlist">
            <tr>
                <td class = "tbl-passage"> Passage
                </td>
                <td class = "num-data">Delete
                </td>
            </tr>
        </table>
        <input type ="button" id="annotate" value="Highlight" />
        <form method="post" id="submitform" action="index.php">
            ID: <input type="text" name="worker_id" >
            <input type="submit" id="submit" value="Submit" name="submit"/>
        </form>
        <div id="query">
        <?php 

            if(isset($_POST['annot'])) {

                $worker_id = $db->real_escape_string($_POST['w_id']);
                
                // check to see if this worker has already submitted an annotation
                $exists_q = "SELECT a_id FROM Annotators where a_name = '" . $worker_id . "';";
                
                $user_id = NULL;

                if ($result = $db->query($exists_q))
                {
                    while ($row = $result->fetch_assoc())
                    {
                        $user_id = $row['a_id'];
                    }
                    
                    $result->free();
                }
                
                if ($user_id == NULL)
                {                
                    //Make new annotator - should be called when the annotate button is clicked
                    $q1 = "INSERT INTO Annotators VALUES (NULL , '" . $worker_id . "');";
                    $q2 = "SELECT LAST_INSERT_ID()";
                    $db->query($q1);
    
                    if ($result = $db->query($q2)) {
                        while ($row = $result->fetch_assoc()) {
                            
                            $user_id = $row['LAST_INSERT_ID()'];
                        }
    
                        $result->free();
                    }
                }
                
                $var = $_POST['annot'];
                $var2 = $_POST['char'];
                $var_string = explode(",", $var);
                $var_string = implode(" ", $var_string);

                $sql = "INSERT INTO Annotations VALUES (NULL , " . $user_id . ", " . $document_id .", '" . $var_string ."', '". $var2 ."');";
                $db->query($sql);


            }

            $db->close();
        ?>
        </div>
        <div id="loading"><h1>Submitting ... </h1></div>
        <div id="afterform">
            <h1>Thank you for submitting your annotations!</h1>
        </div>
    </div>
</body>

</html>