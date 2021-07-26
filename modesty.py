import json
import requests
import os
from rich.console import Console
from time import sleep
from rich.table import Table

console = Console()

os.system('pip install rich -q')


LBC = '''
                       =%#-                       
                    .+@@@@@%=                     
                  :#@@@@#%@@@@*:                  
                -%@@@%#++**#@@@@%-                
              =@@@@%*++++****#@@@@@+.             
           :*@@@@#+=+++++***#%@@@@@@@*:           
         -#@@@@*====+++++*#@@@@%+=*%@@@%=         
       =%@@@%+======+++*%@@@@#=-====+#@@@@+.      
    :*@@@%*+========+*%@@@#+----=======*%@@@#-    
   #@@@%+=========+*@@@@%-------=========+#@@@@.  
   %@@%==========+++*#@@@%+-----=========-:=@@@:  
   %@@%=======+++++++++#@@@%+---=======-:::=@@@:  
   %@@%=====++++++++++++*%@@@@*-====-::::::=@@@:  
   %@@%===+++++++++++++++++#@@@@*--::::::::=@@@:  
   %@@@++++++++++++++++++*#@@@@#=----::::::=@@@:  
   =@@@@%*+++++++++++++*%@@@@*------------*@@@@.  
     -#@@@%#*+++++++*#@@@@#+-----------+#@@@#=    
       .*@@@@#*+++*%@@@@*-----------=#@@@@+.      
         .+@@@@%#@@@@%+====-------+%@@@%=         
            =@@@@@@#+===========*@@@@#-           
              -%@@@#+=========#@@@@*.             
                -%@@@%+====+%@@@@=                
                  -#@@@%**@@@@#-                  
                    :*@@@@@@*:                    
                      .+@#=                        '''



# LBRY JSON RPC URL
HOST = "http://localhost:5279"

# Do a claim list
response = requests.post(HOST, json={"method": "claim_list",
                                     "params": {}}).json()

f = open("modesty_names_output.txt", "w")

# Get the number of claims
num_claims = response["result"]["total_items"]
def write(s, end="\n", flush=False):
    """
    Write a string to stdout and the file
    """
    print(s, end=end, flush=flush)
    f.write(s)
    f.write(end)
    if flush:
        f.flush()
# Get the claim info
write("\n"+ LBC+"\n")
with console.status("[bold green]Looking into LBRY blockchain...", spinner="earth") as status:
    write("\n")
    f.write(f"You have {num_claims} claims.")
    console.print(f"You have {num_claims} claims." + ":smiley:")
    write("If you stake more LBC in the names bellow you can get better viewership on then \n",
        flush=True, end="")
    response = requests.post(HOST,
                            json={"method": "claim_list",
                                "params": {"page_size": num_claims,
                                            "resolve":   True}}).json()
    claims = response["result"]["items"]


    for claim in claims:

        claim_id = claim["claim_id"]

        # Vanity name and whether you're controlling it
        vanity_name = claim["name"]
        controlling = claim["meta"]["is_controlling"]
        staked_amount = float(claim["amount"]) + float(claim["meta"]["support_amount"])

        # Get multiplicity of the vanity name, and max LBC
        max_lbc = None
        response = requests.post(HOST,
                        json={"method": "claim_search",
                            "params": {"name": vanity_name}}).json()
        multiplicity = response["result"]["total_items"]
        response = requests.post(HOST,
                        json={"method": "claim_search",
                            "params": {"name": vanity_name,
                                        "page_size": multiplicity}}).json()

        competitors = 0
        for item in response["result"]["items"]:

            # Look at staked LBC
            item_lbc = float(item["amount"]) + float(item["meta"]["support_amount"])
            if item["claim_id"] != claim_id and \
                    (max_lbc is None or item_lbc > max_lbc):
                max_lbc = round(item_lbc,2)

            # Count competitors
            if (item["value_type"] != "repost" and item["claim_id"] != claim_id)\
                    or ("reposted_claim_id" in item and \
                        item["reposted_claim_id"] == claim_id):
                competitors += 1
    # Print some information
        table = Table()
        table.add_column("Post Name", justify="center", style="bright_yellow", no_wrap=True)
        table.add_column("Winning Bid", justify="center", style="green")
        table.add_column("Your poor Bid", justify="center", style="red")
        

        
        if controlling:
            continue

        else:
            table.add_row(vanity_name, str(max_lbc) +" LBC" , str(staked_amount) +" LBC")

         
            f.write("-------------------------------"+"\n")
            f.write("Name: "+ vanity_name +"\n")
            f.write("-------------------------------"+"\n")
            f.write(f"Number of competing claims, excluding reposts of your claim: {competitors}""\n")
            f.write(f"LBC on your claim: {staked_amount}""\n")
            f.write(f"Maximum LBC on competing claims: {max_lbc}""\n")
            f.write("-------------------------------------------------------------------"+"\n")

        if max_lbc is not None:
            if controlling and max_lbc > staked_amount:
                write("TAKEOVER WARNING!")
            if not controlling and staked_amount > max_lbc:
                write("YOUR CLAIM HAS ENOUGH LBC BUT IS WAITING FOR TAKEOVER.")
                write("", end="\n\n", flush=True)
        f.write("-------------------------------------------------------------------")
        console.rule("[bold red]")
        console.print(table)

f.close()
console.print(f'[bold][red]Done! :heart:'+ ' [yellow]Output saved to modesty_names_output.txt')


