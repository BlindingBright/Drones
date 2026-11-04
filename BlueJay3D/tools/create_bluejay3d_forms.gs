/**
 * Google Apps Script: 1-Click Creator for BlueJay3D Google Forms
 *
 * Creates both official Google Forms for BlueJay3D:
 *   1. BlueJay3D: Request a Build for Your ESC / Board
 *   2. BlueJay3D: Log & Feedback Upload
 *
 * Instructions:
 *   1. Open https://script.google.com and click "New project"
 *   2. Paste this file into Code.gs and click Run -> createBlueJay3DForms
 *   3. Check the Execution Log at the bottom for the two published Form URLs (and short URLs)
 *   4. Note: For the Log Upload Form, Google Apps Script creates a link/folder for uploads or
 *      you can duplicate your BetaFlight 3D Edition Log Upload form in Google Drive so the
 *      native 10-file .BBL File Upload widget is ready immediately.
 */

function createBlueJay3DForms() {
  // 1. Create Target Request Form
  var reqForm = FormApp.create('BlueJay3D - ESC Target & Board Build Request');
  reqForm.setTitle('BlueJay3D: Request a Build for Your ESC / Board');
  reqForm.setDescription(
    "Want to test BlueJay3D on an 8-bit ESC or AIO flight controller that isn't in the list yet " +
    "(or not sure which ESC layout your board uses)? Tell us your board/ESC and we'll identify or " +
    "build a test firmware for it. When it's ready, it gets added to TARGETS.md and we'll contact you.\n\n" +
    "Check the download list first; 135 firmware builds across 63 ESC layouts (EFM8BB1, EFM8BB2, and " +
    "EFM8BB51 at 24/48/96 kHz) are already built. Project page, guide and downloads: " +
    "https://github.com/BlindingBright/Drones/tree/bluejay3d/BlueJay3D\n\n" +
    "Tip: in esc-configurator.com or the Bluejay3D Configurator, click Read Settings. " +
    "The ESC layout code is shown on each ESC (e.g. O_H_5, Z_H_30, A_H_5, G_H_30, or A_X_5)."
  );
  reqForm.setCollectEmail(false);
  reqForm.setRequiresLogin(false);

  reqForm.addTextItem()
    .setTitle('Pilot name / callsign')
    .setRequired(true);

  reqForm.addTextItem()
    .setTitle('How should we contact you when your build is ready? (Discord name or email)')
    .setRequired(true);

  reqForm.addTextItem()
    .setTitle("ESC layout code, exactly as esc-configurator.com shows it (e.g. O_H_5, Z_H_30, B_X_30, or 'Not sure')")
    .setRequired(true);

  reqForm.addTextItem()
    .setTitle('AIO Flight Controller or 4-in-1 ESC manufacturer and product name (a link to the board is great)')
    .setRequired(true);

  reqForm.addMultipleChoiceItem()
    .setTitle('What kind of ESC hardware is it?')
    .setChoiceValues([
      'Built into the board (AIO / whoop / toothpick board)',
      'Separate 4-in-1 ESC',
      'Four individual ESCs',
      'Not sure'
    ])
    .setRequired(true);

  reqForm.addMultipleChoiceItem()
    .setTitle('Current ESC firmware and MCU type')
    .setChoiceValues([
      'Bluejay (EFM8BB21 / _H_ layout)',
      'BLHeli_S (EFM8BB1 / EFM8BB2)',
      'Bluejay / BLHeli_S on EFM8BB51 (_X_ layout)',
      'Not sure'
    ])
    .setRequired(true);

  reqForm.addMultipleChoiceItem()
    .setTitle('Preferred PWM frequency')
    .setChoiceValues([
      '48 kHz (Recommended for 1S/2S whoops & toothpicks)',
      '24 kHz (Recommended for 5-inch & heavy props)',
      '96 kHz',
      'All three (24 / 48 / 96 kHz)'
    ])
    .setRequired(true);

  reqForm.addTextItem()
    .setTitle('Flight controller firmware you fly now (e.g. BetaFlight 3D Edition v0.3.1, Betaflight 4.5.1)')
    .setRequired(false);

  reqForm.addParagraphTextItem()
    .setTitle('Your 3D quad: frame, motors (size + kv), props, battery cells. Have you flown 3D on it already?')
    .setRequired(true);

  reqForm.addMultipleChoiceItem()
    .setTitle('Will you fly the test and send logs? (the point of these builds is getting logs back)')
    .setChoiceValues([
      'Yes: the full 4-pack A/B test from the guide',
      "Yes: I'll fly it and send some logs",
      'Maybe: I mostly want to try it'
    ])
    .setRequired(true);

  reqForm.addParagraphTextItem()
    .setTitle('Anything else we should know? (desync symptoms on stock Bluejay, questions, other boards)')
    .setRequired(false);

  var reqShortUrl = reqForm.shortenFormUrl(reqForm.getPublishedUrl());

  // 2. Create Log & Feedback Upload Form (by duplicating BetaFlight 3D Edition Log Form so File Upload items work)
  var bf3dLogFormId = '1FogE8pFKXeIBI9-ypMe_yrfEz8o_IOBFzjttj1RJlRg';
  var logFile = DriveApp.getFileById(bf3dLogFormId).makeCopy('BlueJay3D - Log & Feedback Upload');
  var logForm = FormApp.openById(logFile.getId());
  logForm.setTitle('BlueJay3D: Log & Feedback Upload');
  logForm.setDescription(
    "Thanks for testing BlueJay3D! Upload your blackbox logs (.BBL) here, along with a few details " +
    "about your ESC/drone and a short report. Every log helps prove (or disprove) the 9 backported " +
    "AM32/ESCape32 3D commutation, braking, and fast-restart fixes across different 8-bit ESCs.\n\n" +
    "Testing guide, firmware, presets, and configurator: " +
    "https://github.com/BlindingBright/Drones/tree/bluejay3d/BlueJay3D\n\n" +
    "File uploads need a Google sign-in (that's how Google Forms handles files). You can upload up to " +
    "10 logs at once. Need a build for a different ESC layout? Request one at " + reqShortUrl +
    " or contact ZoeFPV (Discord link at zoefpv.com)."
  );

  var logShortUrl = logForm.shortenFormUrl(logForm.getPublishedUrl());

  Logger.log('=== BlueJay3D Google Forms Created ===');
  Logger.log('Target Request Form ID  : ' + reqForm.getId());
  Logger.log('Target Request Short URL: ' + reqShortUrl);
  Logger.log('Log Upload Form ID      : ' + logForm.getId());
  Logger.log('Log Upload Short URL    : ' + logShortUrl);
}
