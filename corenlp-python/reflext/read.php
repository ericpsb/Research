<?php 
    $document_id = $_GET['did'];

    $num_rows = 0;

    function add($first, $second) {
        return $first + $second;
    }

    $db = new mysqli("eltanin.cis.cornell.edu", "annotator", "Ann0tateTh!s", "FrameAnnotation");
    $db->set_charset('ISO-8859-1');
    if($db->connect_errno > 0) {
        die('Unable to connect to database [' . $db->connect_error . ']');
    }
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
    $q2 = "SELECT SQL_CALC_FOUND_ROWS *, annotation FROM Annotations WHERE doc_id =". $document_id;
    

    if ($result = $db->query($q2)) {
    	$annotationArray = array();
        $num_rows = $result->num_rows;
        /* fetch associative array */
        while ($row = $result->fetch_assoc()) {
            //$row = $q->fetch_row();

            $annot_boolean = array_map('intval', explode(" ", $row['annotation']));
            $annotationArray = array_map('add', $annotationArray, $annot_boolean);

        }
        $result->free();

        // Can normalize by max value or by num rows 
        $max_val = max($annotationArray);
        foreach ($annotationArray as $val) {
            $normalizedArray[] = ($val) / ($max_val);
        }


    } else {
        die('There was an error running the query [' . $db->error . ']');
    }

    $annotator_annotations = array();
    $q3 = "SELECT Ations.annotation, Ators.a_name 
        FROM Annotations Ations 
        INNER JOIN Annotators Ators
        ON Ations.a_id = Ators.a_id 
        WHERE Ations.doc_id =". $document_id . " order by Ators.a_name";
    if ($result = $db->query($q3)) {
        while ($row = $result->fetch_assoc()) {
            $annotator_annotations[$row['a_name']] = $row['annotation'];
        }
    } else {
        die('There was an error running the query [' . $db->error . ']');
    }
    $result -> free();

    header('Content-Type: text/html; charset=ISO-8859-1');
    $words = explode(" ", $passage);

?>

<script type="text/javascript"> 
    var ator_ations = <?php echo json_encode($annotator_annotations); ?></script>
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
    <script src="http://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
    <script type = "text/javascript" src="read.js"></script>
    <script src="scripts/jquery-1.9.1.js"></script>
    <script src="scripts/jquery-ui-1.10.3.custom.js"></script>
    <link href="css/reset.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">
    <link href="css/smoothness/jquery-ui-1.10.3.custom.css" rel="stylesheet">
</head>

<body>
    <div id="passage">
        <?php for ($i = 0; $i < count($words); $i++) { 
            $str = $words[$i];
            if ($str[0] == "<") {
                print $str;
            } else { 
                print "<span id=s-" . $i . " class=\"space\">&nbsp;</span><span id = " . $i . " class=\"passage_words\" style= 'background: rgba(255, ". (int) (255 * (1.0 - $normalizedArray[$i])) .", 0,". (($normalizedArray[$i] > 0) ? "0.5" : "0") .")'>" . $str . "</span>";
            } 
        } 
        ?>
    </div>
    <div id="annotated">
        <form id = "ator_checkboxes" action="#">
            <input type="checkbox" name = "checkall" id="checkall"/> Check All 
            <br />
            <?php 
            foreach ($annotator_annotations as $name => $annot) {
                print '<input type="checkbox" class="atorcheck" name='.$name.' value='.$name.'/>';
                print $name . '<br />';
            }?>

        </form>
    </div>
</body>
</html>