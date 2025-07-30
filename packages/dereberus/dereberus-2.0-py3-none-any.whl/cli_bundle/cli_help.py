CLI_HELP_MESSAGE = """
\033[1;36m────────────────────────────────────────────────────────────────────
  Dereberus CLI  -  Manage Resource Access & Admin Actions
────────────────────────────────────────────────────────────────────\033[0m

\033[1mUSAGE:\033[0m
  \033[92mdereberus [COMMAND] [OPTIONS]\033[0m

\033[1mAVAILABLE COMMANDS:\033[0m

\033[95m═══════════════════════════════════════════════════════════════════════\033[0m
  \033[93mlogin - \033[0m Authenticate and register your public key.

    Example:\n
      \033[92mdereberus login\033[0m\n

    \033[2mExplanation:\033[0m\n
      Use this to authenticate yourself with Dereberus.\n
      If you haven't registered your public key before, you'll be prompted to provide it.\n
      If you have, you can update it.\n
\033[95m═══════════════════════════════════════════════════════════════════════\033[0m

  \033[93mresource - \033[0m List all available resources.

    Example:\n
      \033[92mdereberus resource\033[0m\n

    \033[2mExplanation:\033[0m\n
      Shows a table of all resources (name & IP) you may request access to.\n
      Use this to find valid resource names for use with the 'access' command.\n
\033[95m═══════════════════════════════════════════════════════════════════════\033[0m

  \033[93maccess - \033[0m Request access to a resource or a service/client.\n

    Examples:\n
      \033[92mdereberus access -r "proboscis" -m "Debugging"\033[0m\n
      \033[92mdereberus access -s "b" -c "dailyneeds" -m "Maintenance"\033[\n

    \033[2mExplanation:\033[0m\n
      Use this command to request access to a resource or to a specific service/client.\n
      For resource access, use -r.\n
      For service/client, use both -s and -c.\n
      Add a message with -m to explain your reason.\n
\033[95m═══════════════════════════════════════════════════════════════════════\033[0m

  \033[93mlist - \033[0m List access requests with filters (admin only).

    Examples:\n
      \033[92mdereberus list\033[0m\n
      \033[92mdereberus list -m all\033[0m\n
      \033[92mdereberus list -m approved\033[0m\n
      \033[92mdereberus list -m all -n 3\033[0m\n

    \033[2mExplanation:\033[0m\n
      Admins can see all access requests.\n
      Filter by status with mode, use -m (pending/approved/all).\n
      Limit to requests from the last N days with -n.\n
\033[95m═══════════════════════════════════════════════════════════════════════\033[0m

  \033[93mapprove - \033[0m Approve a specific request (admin only).

    Example:\n
      \033[92mdereberus approve -i 42\033[0m\n

    \033[2mExplanation:\033[0m\n
      Admins use this to approve an access request by specifying its request ID.\n
\033[95m═══════════════════════════════════════════════════════════════════════\033[0m

  \033[93mreject - \033[0m Reject a specific request (admin only).

    Example:\n
      \033[92mdereberus reject -i 43\033[0m\n

    \033[2mExplanation:\033[0m\n
      Admins use this to reject an access request by specifying its request ID.\n
\033[95m═════════════════════════════════════════════════════════════════════\033[0m

\033[1mTIP:\033[0m\n
  Use '\033[92mdereberus <command> --help\033[0m' to view details for each command.
"""