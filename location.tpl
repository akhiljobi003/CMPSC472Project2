<html>
<head>
<title>Rehab Treatment centers location finder</title>
</head>
<body style="display: flex; justify-content: center; align-items: center;height:100%; background: #bdc3c7;">
<div style="width: 50%;">
<H1>Location of the centers near {{loc}}</H1>
<H2>Nearest</H2>
<H3> Latitude: {{latitude}} longitude: {{longitude}}</H3>
<p>Rest of the places:<br>
%for key in rest:
    %try:
        %for x in key:
            %try:
                Place: {{ x[0] }}<br>
                Distance: {{ x[1] }}<br>
            %except KeyError:
                %continue
            %end
        %end
    %except KeyError:
        %continue
    %end
%end

</p>
</div>
</body>
</html>
