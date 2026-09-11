<?php
/**
 * Traitement du formulaire de contact — envoi direct par mail() PHP,
 * sans service tiers. Destinataire fixe (jamais pris depuis le formulaire).
 */
declare(strict_types=1);

$destinataire = 'lou@etudesbois.fr';
$site         = 'etudesbois.fr';

function veut_json(): bool {
    return isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false;
}

function repondre(bool $succes, string $message): void {
    if (veut_json()) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['success' => $succes, 'message' => $message]);
    } else {
        header('Location: /?envoye=' . ($succes ? '1' : '0') . '#ecrire');
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /#ecrire');
    exit;
}

// pot de miel anti-spam : un vrai visiteur laisse ce champ vide
if (!empty($_POST['_honey'])) {
    repondre(true, 'ok'); // on fait comme si de rien n'etait, sans envoyer
}

$nom         = trim((string)($_POST['nom'] ?? ''));
$coordonnees = trim((string)($_POST['coordonnees'] ?? ''));
$message     = trim((string)($_POST['message'] ?? ''));

if ($nom === '' || $coordonnees === '' || $message === '') {
    repondre(false, 'Merci de remplir tous les champs.');
}
if (mb_strlen($nom) > 200 || mb_strlen($coordonnees) > 200 || mb_strlen($message) > 8000) {
    repondre(false, 'Message trop long.');
}

// nettoyage minimal (les en-tetes mail() ne doivent jamais recevoir de retour a la ligne)
$sans_injection = static fn(string $s): string => str_replace(["\r", "\n"], ' ', $s);
$nom_s = $sans_injection($nom);
$coord_s = $sans_injection($coordonnees);

$sujet = "Nouveau message depuis $site";
$corps = "Nouveau message via le formulaire de $site :\n\n"
       . "Nom : $nom_s\n"
       . "Coordonnees : $coord_s\n\n"
       . "Message :\n$message\n";

// Reply-To = coordonnees du visiteur si ca ressemble a un e-mail, sinon rien
$entetes = "From: Site $site <no-reply@$site>\r\n";
if (filter_var($coordonnees, FILTER_VALIDATE_EMAIL)) {
    $entetes .= "Reply-To: $coord_s\r\n";
}

$ok = @mail($destinataire, $sujet, $corps, $entetes);

repondre($ok, $ok ? 'Message envoye.' : "L'envoi a echoue.");
