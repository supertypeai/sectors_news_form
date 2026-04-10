from typing import Optional 


def generate_title_and_body(
    holder_name: str,
    company_name: str,
    tx_type: str,
    amount: Optional[int],
    holding_before: Optional[int],
    holding_after: Optional[int],
    purpose_en: str,
) -> tuple[str, str]:
    
    if tx_type:
        action_title = tx_type.title()
    else: 
        tx_type = None 
        action_title = None 

    if holder_name:
        holder_name = holder_name.title()

    if tx_type == "buy":
        action_verb = "bought"
        title = f"{holder_name} buys shares of {company_name}"
    
    elif tx_type == "sell":
        action_verb = "sold"
        title = f"{holder_name} sells shares of {company_name}"
    
    elif tx_type == "share-transfer":
        action_verb = "transferred"
        title = f"{holder_name} transfers shares of {company_name}"

    elif tx_type == 'transfer': 
        action_verb = "executed a transaction for"
        title = f"{holder_name} share movement in {company_name}"

    elif tx_type == "award":
        action_verb = "was awarded"
        title = f"{holder_name} was awarded shares of {company_name}"
    
    elif tx_type == "others": 
        action_verb = "executed a transaction for"
        title = f"Change in {holder_name}'s position in {company_name}"
    
    elif tx_type == "inheritance":
        action_verb = "inherited"
        title = f"{holder_name} inherits shares of {company_name}"
    
    else:
        action_verb = "executed a transaction for"
        title = f"{holder_name} {action_title} transaction of {company_name}"

    amount_str = f"{amount:,} shares" if amount is not None else "shares"
    body = f"{holder_name} {action_verb} {amount_str} of {company_name}."

    if holding_before is not None and holding_after is not None:
        hb_str, ha_str = f"{holding_before:,}", f"{holding_after:,}"
        if holding_after > holding_before:
            body += f" This increases their holdings from {hb_str} to {ha_str} shares."
        elif holding_after < holding_before:
            body += f" This decreases their holdings from {hb_str} to {ha_str} shares."
        else:
            body += f" Their holdings remain at {ha_str} shares."

    if purpose_en:
        body += f" The stated purpose of the transaction was {purpose_en.lower()}."
    return title, body