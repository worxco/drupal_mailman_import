<?php

/*
 * Get the vid for our vocabulary
 */
$x = taxonomy_get_vocabularies();
foreach ($x as $tax) {
  if ($tax->name == 'ListServ') {
    $vid = $tax->vid;
  }
}

/*
 * Open the temp file for the transfer of the email
 * fgets will read one line at a time, so the order below is critical
 * fread is designed to read ALL the rest of the record and we put the body last.
 */
$fd = fopen('/tmp/listservmov', 'r');
$tax = trim( fgets( $fd ));
$path = trim( fgets( $fd ));
$file = trim( fgets( $fd ));
$postdate = trim( fgets( $fd ));
$name = trim( fgets( $fd ));
$email = trim( fgets( $fd ));
$title = trim( fgets( $fd ));
$body = fread( $fd, 99999 );


/*
 * See if we already have this user. If we do not....
 * Create the user as a 'disabled' user with no roles beyond 'authenticated'.
 * We lookup the user by email address first.
 * If no record exists, we then check by name.
 * If the name exists, we ignore the 'alias' email and continue.
 * If neither name or email exists, we create a new user record.
 */
$existing_user = user_load(array('mail' => $email, 'name' => $name));
if (isset($existing_user->uid)) {
  $user = $existing_user;
} else {
  $existing_user = user_load(array('name' => $name));
  if (isset($existing_user->uid)) {
    $user = $existing_user;
  } else {
    $userinfo = array(
      'name' => $name,
      'init' => $name,
      'status' => 0,
      'mail' => $email,
      'access' => time()
    );
    $account = user_save('', $userinfo);
    if (!$account) {
      drupal_Set_message(t("Error saving user account."), 'error');
    }
    $user = $account;
    watchdog('user', 'New user created by mailman import: %name', array( '%name' => $name ), WATCHDOG_NOTICE, l(t('edit'), 'user/'. $user->uid .'/edit'));
  }
}

/*
 * Time to build the 'listserve' node.
 * We use the name of the list as a taxonomy term.
 * We convert the postdate to the creation time.
 * We assign the uid from the user found/created above to assign the email to the responsible party.
 * Turn off any ability to add comments
 * Set this format to 'full-html'
 * Title and Body speak for themselves.
 */
$node = new stdClass();
$node->taxonomy['tags'][$vid] = $tax;
$node->type = 'listserve';
$node->uid = $user->uid;
$node->created = strtotime($postdate);
$node->title = $title;
$node->body = $body;
$node->comment = 0;
$node->format = 2; 
node_save($node);
 
/*
 * We build a url-alias equivilant to the original url to the mail entry
 */
if ($node->nid) {
  path_set_alias('node/' . $node->nid, 'listserv/'. $path, NULL, 'en');
}
