from dotenv import load_dotenv

from app.scripts.aws.main_vm import run_aws_vm_main
# from app.scripts.aws.test_vm import run_aws_vm_test
# from app.scripts.azure.vm import run_azure_vm
# from app.scripts.gcp.msec_001_vm import run_gcp_msec_001_vm_main
# from app.scripts.gcp.test_vm import run_gcp_test_vm_main
# from app.scripts.gcp.scared_atom_vm import run_gcp_scared_atom_vm_main

# Call the function from aws_cost_main.py
run_aws_vm_main()
# run_aws_vm_test()
# run_azure_vm()
# run_gcp_test_vm_main()
# run_gcp_msec_001_vm_main()
# run_gcp_scared_atom_vm_main()
