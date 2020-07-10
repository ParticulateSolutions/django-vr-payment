import re

"""
checks for VR Payment result codes

see https://vr-pay-ecommerce.docs.oppwa.com/reference/resultCodes for full list
"""

TRANSACTION_SUCCESSFULLY_PROCESSED_REGEX = r"^(000\.000\.|000\.100\.1|000\.[36])"
TRANSACTION_SUCCESSFULLY_PROCESSED_NEEDS_REVIEW_REGEX = (
    r"^(000\.400\.0[^3]|000\.400\.100)"
)
TRANSACTION_PENDING_REGEX = r"^(000\.200)"
TRANSACTION_PENDING_MIGHT_CHANGE_EXTERNALLY_REGEX = r"^(800\.400\.5|100\.400\.500)"


def check_transaction_status(regex, result_code: str) -> bool:
    return True if re.search(regex, result_code) else False


def check_transaction_successful(result_code: str) -> bool:
    """
    shortcut to see if the transaction was successful.
    NOTE: might be best to check separately for check_transaction_successfully_processed_needs_review
    """
    return check_transaction_successfully_processed(
        result_code
    ) or check_transaction_successfully_processed_needs_review(result_code)


def check_transaction_pending(result_code: str) -> bool:
    """
    shortcut to see if the transaction is pending.
    """
    return check_transaction_pending(
        result_code
    ) or check_transaction_pending_might_change_externally(result_code)


def check_transaction_rejected(result_code: str) -> bool:
    """
    shortcut to see if the transaction was rejected.
    """
    return (
        check_transaction_rejected_3dsecure_risk(result_code)
        or check_transaction_rejected_bank(result_code)
        or check_transaction_rejected_communications_error(result_code)
        or check_transaction_rejected_systems_error(result_code)
        or check_transaction_rejected_async_error(result_code)
        or check_transaction_rejected_soft_decline(result_code)
        or check_transaction_rejected_risk_handling_external_risk_system(result_code)
        or check_transaction_rejected_risk_handling_address_validation(result_code)
        or check_transaction_rejected_risk_handling_3dsecure(result_code)
        or check_transaction_rejected_risk_handling_blacklist_validation(result_code)
        or check_transaction_rejected_risk_handling_risk_validation(result_code)
        or check_transaction_rejected_configuration_validation(result_code)
        or check_transaction_rejected_registration_validation(result_code)
        or check_transaction_rejected_job_validation(result_code)
        or check_transaction_rejected_reference_validation(result_code)
        or check_transaction_rejected_format_validation(result_code)
        or check_transaction_rejected_address_validation(result_code)
        or check_transaction_rejected_contact_validation(result_code)
        or check_transaction_rejected_account_validation(result_code)
        or check_transaction_rejected_amount_validation(result_code)
        or check_transaction_rejected_risk_management(result_code)
    )


########################################################
#                                                      #
# Result codes for successful and pending transactions #
#                                                      #
########################################################


def check_transaction_successfully_processed(result_code: str) -> bool:
    """
    Result codes for successfully processed transactions

    The regular expression pattern for filtering out this group is: /^(000\.000\.|000\.100\.1|000\.[36])/
    """
    return check_transaction_status(
        TRANSACTION_SUCCESSFULLY_PROCESSED_REGEX, result_code
    )


def check_transaction_successfully_processed_needs_review(result_code: str) -> bool:
    """
    Result codes for successfully processed transactions that should be manually reviewed

    The regular expression pattern for filtering out this group is: /^(000\.400\.0[^3]|000\.400\.100)/

    """
    return check_transaction_status(
        TRANSACTION_SUCCESSFULLY_PROCESSED_NEEDS_REVIEW_REGEX, result_code
    )


def check_transaction_pending(result_code: str) -> bool:
    """
    Result codes for pending transactions

    The regular expression pattern for filtering out this group is: /^(000\.200)/. These codes mean that there is an open session in the background, meaning within half an hour there will be a status change, if nothing else happens, to timeout.
    """
    return check_transaction_status(TRANSACTION_PENDING_REGEX, result_code)


def check_transaction_pending_might_change_externally(result_code: str) -> bool:
    """
    Result codes for pending transactions

    There is another kind of pending regular expression pattern for filtering out this group is: /^(800\.400\.5|100\.400\.500)/. These codes describe a situation where the status of a transaction can change even after several days."""
    return check_transaction_status(
        TRANSACTION_PENDING_MIGHT_CHANGE_EXTERNALLY_REGEX, result_code
    )


##########################################
#                                        #
# Result codes for rejected transactions #
#                                        #
##########################################


def check_transaction_rejected_3dsecure_risk(result_code: str) -> bool:
    """
    Result codes for rejections due to 3Dsecure and Intercard risk checks

    The regular expression pattern for filtering out this group is: /^(000\.400\.[1][0-9][1-9]|000\.400\.2)/
    """
    regex = r"^(000\.400\.[1][0-9][1-9]|000\.400\.2)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_bank(result_code: str) -> bool:
    """
    Result codes for rejections by the external bank or similar payment system

    The regular expression pattern for filtering out this group is: /^(800\.[17]00|800\.800\.[123])/
    """
    regex = r"^(800\.[17]00|800\.800\.[123])"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_communications_error(result_code: str) -> bool:
    """
    Result codes for rejections due to communication errors

    The regular expression pattern for filtering out this group is: /^(900\.[1234]00|000\.400\.030)/
    """
    regex = r"^(900\.[1234]00|000\.400\.030)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_systems_error(result_code: str) -> bool:
    """
    Result codes for rejections due to system errors

    The regular expression pattern for filtering out this group is: /^(800\.[56]|999\.|600\.1|800\.800\.[84])/
    """
    regex = r"^(800\.[56]|999\.|600\.1|800\.800\.[84])"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_async_error(result_code: str) -> bool:
    """
    Result codes for rejections due to error in asynchonous workflow

    The regular expression pattern for filtering out this group is: /^(100\.39[765])/
    """
    regex = r"^(100\.39[765])"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_soft_decline(result_code: str) -> bool:
    """
    Result codes for Soft Declines

    The regular expression pattern for filtering out this group is: /^(300\.100\.100)/
    """
    regex = r"^(300\.100\.100)"
    return check_transaction_status(regex, result_code)


########################################
#                                      #
# Rejections specific to risk handling #
#                                      #
########################################


def check_transaction_rejected_risk_handling_external_risk_system(
    result_code: str,
) -> bool:
    """
    Result codes for rejections due to checks by external risk systems

    The regular expression pattern for filtering out this group is: /^(100\.400\.[0-3]|100\.38|100\.370\.100|100\.370\.11)/
    """
    regex = r"^(100\.400\.[0-3]|100\.38|100\.370\.100|100\.370\.11)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_risk_handling_address_validation(
    result_code: str,
) -> bool:
    """
    Result codes for rejections due to address validation

    The regular expression pattern for filtering out this group is: /^(800\.400\.1)/
    """
    regex = r"^(800\.400\.1)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_risk_handling_3dsecure(result_code: str) -> bool:
    """
    Result codes for rejections due to 3Dsecure

    The regular expression pattern for filtering out this group is: /^(800\.400\.2|100\.380\.4|100\.390)/
    """
    regex = r"^(800\.400\.2|100\.380\.4|100\.390)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_risk_handling_blacklist_validation(
    result_code: str,
) -> bool:
    """
    Result codes for rejections due to blacklist validation

    The regular expression pattern for filtering out this group is: /^(100\.100\.701|800\.[32])/
    """
    regex = r"^(100\.100\.701|800\.[32])"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_risk_handling_risk_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to risk validation

    The regular expression pattern for filtering out this group is: /^(800\.1[123456]0)/
    """
    regex = r"^(800\.1[123456]0)"
    return check_transaction_status(regex, result_code)


#################################################
#                                               #
# Result codes for rejections due to validation #
#                                               #
#################################################


def check_transaction_rejected_configuration_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to configuration validation

    The regular expression pattern for filtering out this group is: /^(600\.[23]|500\.[12]|800\.121)/
    """
    regex = r"^(600\.[23]|500\.[12]|800\.121)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_registration_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to registration validation

    The regular expression pattern for filtering out this group is: /^(100\.[13]50)/
    """
    regex = r"^(100\.[13]50)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_job_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to job validation

    The regular expression pattern for filtering out this group is: /^(100\.250|100\.360)/
    """
    regex = r"^(100\.250|100\.360)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_reference_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to reference validation

    The regular expression pattern for filtering out this group is: /^(700\.[1345][05]0)/
    """
    regex = r"^(700\.[1345][05]0)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_format_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to format validation

    The regular expression pattern for filtering out this group is: /^(200\.[123]|100\.[53][07]|800\.900|100\.[69]00\.500)/
    """
    regex = r"^(200\.[123]|100\.[53][07]|800\.900|100\.[69]00\.500)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_address_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to address validation

    The regular expression pattern for filtering out this group is: /^(100\.800)/
    """
    regex = r"^(100\.800)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_contact_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to contact validation

    The regular expression pattern for filtering out this group is: /^(100\.[97]00)/
    """
    regex = r"^(100\.[97]00)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_account_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to account validation

    The regular expression pattern for filtering out this group is: /^(100\.100|100.2[01])/
    """
    regex = r"^(100\.100|100.2[01])"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_amount_validation(result_code: str) -> bool:
    """
    Result codes for rejections due to amount validation

    The regular expression pattern for filtering out this group is: /^(100\.55)/
    """
    regex = r"^(100\.55)"
    return check_transaction_status(regex, result_code)


def check_transaction_rejected_risk_management(result_code: str) -> bool:
    """
    Result codes for rejections due to risk management

    The regular expression pattern for filtering out this group is: /^(100\.380\.[23]|100\.380\.101)/
    """
    regex = r"^(100\.380\.[23]|100\.380\.101)"
    return check_transaction_status(regex, result_code)


###################################
#                                 #
# Chargeback related result codes #
#                                 #
###################################


def check_chargeback_related(result_code: str) -> bool:
    """
    Chargeback related result codes

    The regular expression pattern for filtering out this group is: /^(000\.100\.2)/
    """
    regex = r"^(000\.100\.2)"
    return check_transaction_status(regex, result_code)
