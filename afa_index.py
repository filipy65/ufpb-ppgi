#!/usr/bin/env python3


import datetime
import afa_log


# Display the page.
print("Content-Type: text/html")
print()
print(f"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        {afa_log.html_page_head}
        <title>Archive Fixity Anchor - {afa_log.log_title}</title>
        <style>

table {{
   border-collapse: collapse;
   width: 100%;
}}
td, th {{
    border: 1px solid #000000;
    text-align: center;
    padding: 4px;
}}
tr:nth-child(even) {{
  background-color: #eeeeee;
}}

        </style>
       
    </head>
    <body>
        <h1>Archive Fixity Anchor</h1>
        <h2>Operation: {afa_log.log_title}</h2>
""")

if afa_log.log_info:
    print(f"""
        <fieldset>
            <legend>Message</legend>
            <p style="color:red">{afa_log.log_info}</p>
            <p></p>
        </fieldset>
    """)
    
print(f"""
        <fieldset>
            <legend>Menu</legend>
            <ol>
                <li><a href="?page_to_manage=all&entry_to_audit=all">Execute full audit (audit entries and pages)</a></li>
                <li><form action="?"><button type="submit">Edit or audit entries on page:</button><input type="number" name="page_to_manage" size="3" value="0"></form></li>
                <li><a href="?page_to_manage=open">Create new entries</a></li>
            </ol>
        </fieldset>
        <fieldset>
            <legend>Book information</legend>
            <p>Total closed pages: {afa_log.pages_status['current_page']}</p>
            <p>Not registered closed pages: {len(afa_log.pages_status['not_registered_closed_pages'])} =>
""")

for page_id in afa_log.pages_status['not_registered_closed_pages']:
    print(f" [<a href='?register_page={page_id}'>{page_id}</a>]")
    
print(f"""
            </p>
            <p>Registered pages awaiting confirmation: {len(afa_log.pages_status['registered_pages_awaiting_confirmation'])} =>
""")

for page_id in afa_log.pages_status['registered_pages_awaiting_confirmation']:
    print(f" [<a href='?register_page={page_id}'>{page_id}</a>]")
    
print(f"""
            </p>
            <p>Inconsistent pages: {len(afa_log.pages_status['inconsistent_pages'])} => {afa_log.pages_status['inconsistent_pages']}</p>
            <p>Inconsistent entries (Page ID: [Entries ID]): {afa_log.pages_status['inconsistent_entries']}</p>
        </fieldset>
""")

if isinstance(afa_log.page_to_manage, int):
    print(f"""
        <fieldset>
            <legend>Page information</legend>
            <p>ID: {afa_log.page_to_manage}</p>
            <p>Anchors: {("Root Hash (" + afa_log.log_page['anchors']['hash'] + ") anchored on <a href='https://blockstream.info/testnet/tx/" + afa_log.log_page['anchors']['txid'] + "'>Bitcoin " + afa_log.log_page['anchors']['network'] + "</a></p>") if afa_log.log_page['anchors']['hash'] else "Not available yet</p>"}
            <p>Timestamp: {datetime.datetime.utcfromtimestamp(afa_log.log_page['anchors']['timestamp']).strftime('%Y-%m-%dT%H:%M:%SZ') if afa_log.log_page['anchors']['timestamp'] else "Not available yet"}</p>
            <p>Consistent? {"Yes" if afa_log.log_page['consistent'] and (str(afa_log.page_to_manage) not in afa_log.pages_status['inconsistent_entries']) else '<span style="color:red;font-weight:bold;">NO</span>'} 
            {'(<a href="?page_to_manage=' + str(afa_log.page_to_manage) + '&entry_to_audit=all">Audit this page</a>)' if afa_log.page_to_manage != afa_log.pages_status['current_page'] and afa_log.page_to_manage not in afa_log.pages_status['not_registered_closed_pages'] and afa_log.page_to_manage not in afa_log.pages_status['registered_pages_awaiting_confirmation'] else ""}
            </p>
        </fieldset>
    """)

if afa_log.log_title == f"Edit or audit entries on page {afa_log.page_to_manage}":
    print(f"""
        <fieldset>
            <legend>Entries information</legend>
            <table>
                <tr>
                    <th>Local ID</th>
                    <th>Global ID</th>
                    <th>Description<br>(Text or File path)</th>
                    <th>Hash</th>
                    <th>Replacement Entry<br>(Page ID/Local ID)</th>
                    <th>Consistent</th>
                </tr>
    """)
    for entry in range(afa_log.log_page_total_entries):
        print(f"""
                <tr>
                    <td><input name="local_id" value="{entry}" size="3" readonly></td>
                    <td>{afa_log.log_page['entries']['global_id'][entry]}</td>
                    <td>{'<span style="font-weight:bold;">path:</span>' if afa_log.log_page['entries']['description']['is_file_path'][entry] else ""}{afa_log.log_page['entries']['description']['content'][entry]}</td>
                    <td style="word-break: break-word">{afa_log.log_page['entries']['fixity']['hash'][entry]}</td>
                    <td><form action="?page_to_manage={afa_log.page_to_manage}" method="post">
                        Entry replaced? <input type="checkbox" name="entry_replaced" value="True" {"checked" if afa_log.log_page['entries']['replacement']['replaced'][entry] else ""}>Yes<br>
                        <input name="replace_page" value="{afa_log.log_page['entries']['replacement']['replace_page'][entry]}" size="3">/
                        <input name="replace_id" value="{afa_log.log_page['entries']['replacement']['replace_id'][entry]}" size="3">
                        <button type="submit">Update entry</button></form>
                    </td>
                    <td>{"Yes" if afa_log.log_page['consistent'] and afa_log.log_page['entries']['consistent'][entry] else '<span style="color:red;font-weight:bold;">NO</span>'}</td>
                </tr>
        """)
    print(f"""
            </table>
        </fieldset>
    """)

elif afa_log.log_title == "Create new entries":
    print(f"""
        <fieldset>
            <legend>Create entry</legend>
            <form action="?page_to_manage=open" method="post">
                <input name="local_id" value="ID {afa_log.log_page_total_entries}" size="3" readonly>
                <input name="global_id" placeholder="Global ID" size="20">
                <input name="description" placeholder="Description (text or file path)" size="20">
                Description is a file path? <input type="checkbox" name="description_is_a_file_path" value="True">Yes
                <button type="submit">Register entry</button>
                <button type="reset">Clear form</button>
                OR <a href="?page_to_manage=close">Close page</a>
            </form>
        </fieldset>
        <fieldset>
            <legend>Entries information</legend>
            <table>
                <tr>
                    <th>Local ID</th>
                    <th>Global ID</th>
                    <th>Description<br>(Text or File path)</th>
                    <th>Hash</th>
                </tr>
    """)
    for entry in range(afa_log.log_page_total_entries - 1, -1, -1):
        print(f"""
                <tr>
                    <td>{entry}</td>
                    <td>{afa_log.log_page['entries']['global_id'][entry]}</td>
                    <td>{'<span style="font-weight:bold;">path:</span>' if afa_log.log_page['entries']['description']['is_file_path'][entry] else ""}{afa_log.log_page['entries']['description']['content'][entry]}</td>
                    <td style="word-break: break-word">{afa_log.log_page['entries']['fixity']['hash'][entry]}</td>
                </tr>
        """)
    print(f"""
            </table>
        </fieldset>
    """)
    
print(f"""
    </body>
</html>
""")

