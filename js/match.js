let matching_data = null;
function handleData(data) {{
    matching_data = data;
    console.log("Received JSON data:", matching_data);
    const parentDocument = window.parent.document;
    parentDocument.getElementById('num_of_result').innerHTML = matching_data.length;
    loadJoblist();
}}

function loadJoblist() {{
    const parentDocument = window.parent.document;
    let left_pane = parentDocument.getElementsByClassName('st-key-left-pane')[0]
    let html = "";

    for(let index = 0; index < matching_data.length; index++) {{
        const job = matching_data[index]
        const details = job['details'];
        html += "<div class='job-row'>";
        html += "<a href='javascript:void(0);' target='_self' class='job-detail-link' onClick='document.querySelector(\"iframe\").contentWindow.loadAJob(" + index + ")'>";
        html += "<div class='job-title'>" + details['job_title_base'].join('<br>') + "</div>";
        if(details['company_name'] && details['company_name'].length > 0) {{
            html += "<div class='job-company'>at " + details['company_name'].join('<br>') + "</div>";
        }}
        const locationAry = [];
        for(const location of details['location']) {{
            if(location['city'] || location['state']) {{
                let loc = [];
                if(location['city']) {{
                    loc.push(location['city']);
                }}
                if(location['state']) {{
                    loc.push(location['state']);
                }}
                locationAry.push(loc.join(", "));
            }}
        }}
        let locationStr = 'N/A';
        if(locationAry.length > 0) {
            locationStr = locationAry.join("<br>");
        }

        html += "<div class='job-location'>Location: " + locationStr + "</div>";
        const overall_score = Math.trunc(job['match_scores']['overall_score']*100).toLocaleString('en-US');
        html += "<div class='job-scores'>Overall Scores: " + overall_score + "</div>";
        html += "</a>";
        html += "</div>";
    }}

    left_pane.innerHTML = html;

    loadAJob(0)
}}

function loadAJob(index) {{
    console.log(index);
    const parentDocument = window.parent.document;
    let job_list = parentDocument.getElementsByClassName('job-row');

    for(let i = 0; i < job_list.length; i++) {{
        job_list[i].classList.remove('selected');
        if(i == index) {{
            job_list[i].classList.add('selected');
        }}
    }}
    let right_pane = parentDocument.getElementsByClassName('st-key-match-middle-container')[0];
    const job = matching_data[index]
    let html = ""
    if(job) {{
        const score = job["match_scores"]
        const details = job["details"]
        const mandatory = job["mandatory"]
        const preferred = job["preferred"]
        let company_name = "";
        if(details['company_name'] && details['company_name'].length > 0) {{
            company_name = " at " + details['company_name'].join('<br>');
        }}
        html += "<h3>" + details['job_title_base'].join(", ") + company_name + "</h3>";
        if("overall_score" in score && score["overall_score"]) {{
            html += "<div class='overall_score_header'>✅ Overall = " + Math.trunc(score["overall_score"]*100).toLocaleString('en-US') + "%</div>"
        }}
        if("overall_skills" in score && score["overall_skills"]) {{
            html += "<li class='score_item'>🤹🏽 Skill Score: " + Math.trunc(score["overall_skills"]*100).toLocaleString('en-US') + "%</li>"
        }}
        if("overall_background" in score && score["overall_background"]) {{
            html += "<li class='score_item'>🧮 Background Score: " + Math.trunc(score["overall_background"]*100).toLocaleString('en-US') + "%</li>"
        }}
        if("overall_education" in score && score["overall_education"]) {{
            html += "<li class='score_item'>📒 Education Score: " + Math.trunc(score["overall_education"]*100).toLocaleString('en-US') + "%</li>"
        }}
        if("overall_credentials" in score && score["overall_credentials"]) {{
            html += "<li class='score_item'>📑 Credentials Score: " + Math.trunc(score["overall_credentials"]*100).toLocaleString('en-US') + "%</li>"
        }}
        html += "<div class='score_pane'><div class='score_pane_column'>";
        html += getScoreHtml(score, "mandatory");
        html += "</div><div class='score_pane_column'>";
        html += getScoreHtml(score, "preferred");
        html += "</div><div class='score_pane_column'>";
        if("responsibilities_score" in score && score["responsibilities_score"]) {{
            html += "<div class='score_header'>Responsibilites = " + Math.trunc(score["responsibilities_score"]*100).toLocaleString('en-US') + "%</div>"
        }}   
        html += "</div></div>";
        const locationAry = [];
        for(const location of details['location']) {{
            if(location['city'] || location['state']) {{
                let loc = [];
                if(location['city']) {{
                    loc.push(location['city']);
                }}
                if(location['state']) {{
                    loc.push(location['state']);
                }}
                locationAry.push(loc.join(", "));
            }}
        }}
        let locationStr = 'N/A';
        if(locationAry.length > 0) {
            locationStr = locationAry.join("; ");
        }

        html += "<div id='job-location'><span id='location-label'>Location:</span> " + locationStr + "</div>";
        if(score["overall_mandatory"]) {{
            html += getDetails(mandatory, "👍🏼 Mandatory");
        }}
        if(score["overall_preferred"]) {{
            html += getDetails(preferred, "👏🏼 Preferred");
        }}
    }} else {{
        html = "";
    }}

    right_pane.innerHTML = html;
}}

function getScoreHtml(data, prefix) {
    html = "";

    if("overall_" + prefix in data && data["overall_" + prefix]) {{
        html += "<div class='score_header'>" + prefix.substring(0,1).toUpperCase() + prefix.substring(1) + " = " + Math.trunc(data["overall_" + prefix]*100).toLocaleString('en-US') + "%</div>"
    }}    
    if(prefix + "_skill_score" in data && data[prefix + "_skill_score"]) {{
        html += "<li class='score_item'>🤹🏽 Skill Score: " + Math.trunc(data[prefix + "_skill_score"]*100).toLocaleString('en-US') + "%</li>"
    }}    
    if(prefix + "_background_score" in data && data[prefix + "_background_score"]) {{
        html += "<li class='score_item'>🧮 Background Score: " + Math.trunc(data[prefix + "_background_score"]*100).toLocaleString('en-US') + "%</li>"
    }}
    if(prefix + "_education_score" in data && data[prefix + "_education_score"]) {{
        html += "<li class='score_item'>📒 Education Score: " + Math.trunc(data[prefix + "_education_score"]*100).toLocaleString('en-US') + "%</li>"
    }}
    if(prefix + "_credentials_score" in data && data[prefix + "_credentials_score"]) {{
        html += "<li class='score_item'>📑 Credentials Score: " + Math.trunc(data[prefix + "_credentials_score"]*100).toLocaleString('en-US') + "%</li>"
    }}

    return html;
}

function getDetails(data, title) {{
    let html = '';
    if(data) {{
        html += "<h3>" + title + " Qualifications</h3>";
        const hard_skills = data["hard_skills"];

        if(hard_skills) {{
            html += "<div class='skill-title'>Hard Skills:</div>";
            for(let hard_skill of hard_skills) {{
                let max_year = Math.max(hard_skill["minyears"]);
                let min_year = Math.min(hard_skill["minyears"]);
                if(max_year > 0) {{
                    if(min_year > 0 && max_year != min_year) {{
                        exp_year = min_year + "-" + max_year;
                    }} else {{
                        exp_year = max_year + "+";
                    }}
                    html += "<li class='skill-item'>" + exp_year + " years of " + hard_skill["skill"].flat().join(", ") + "</li>";
                }} else if(hard_skill["skill"].length > 0) {{
                    html += "<li class='skill-item'>" + hard_skill["skill"].flat().join(", ") + "</li>";
                }}
            }}
        }}
        if("education" in data && data["education"].length > 0) {{
            const education = data["education"][0];
            console.log(education);
            // related field, education level
            if("education_level" in education && education["education_level"].length > 0) {{
                let edu_level = education["education_level"].flat().join(", ");
                let fields = "";
                if("field_of_study" in education && education["field_of_study"].length > 0) {{
                    fields = " in " + education["field_of_study"].flat().join(", ") + " Field";
                }}
                html += "<div class='skill-item'><span class='skill-title'>Education:</span> " + edu_level + fields + "</div>";    
            }}
            
        }}
    }}

    return html;
}}