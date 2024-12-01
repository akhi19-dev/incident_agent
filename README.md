# incident_agent

# Steps to Run the Application

1. **Start ngrok on port 8080:**
   ngrok http 8080

2. **Copy the generated ngrok URI**  
   After running the above command, ngrok will provide a public URL in the terminal. Copy this URL.

3. **Update the webhook URI in the following locations:**
   - **Azure Action Group Webhook URI:**
     Replace the webhook URI with your ngrok URL in the Azure portal:
     https://portal.azure.com/#view/Microsoft_Azure_Monitoring_Alerts/EditActionGroupBlade/actionGroupId/%2Fsubscriptions%2F8A73585C-429C-4438-900A-3202DC668D02%2FresourceGroups%2Fnva_auto_resolve_demo_rg%2Fproviders%2Fmicrosoft.insights%2Factiongroups%2Fnva_actions
   - **ServiceNow Webhook URI:**
     Replace the webhook URI with your ngrok URL in the ServiceNow portal:
     https://dev209832.service-now.com/now/nav/ui/classic/params/target/sys_script.do%3Fsys_id%3D209f5eafc3ced690c271554d050131b9%26sysparm_record_target%3Dsys_script%26sysparm_record_row%3D1%26sysparm_record_rows%3D5391%26sysparm_record_list%3DORDERBYDESCsys_updated_on

4. **Start the FastAPI application:**
   uvicorn main:app --port 8080
