from __future__ import annotations

from .types import Decision


def explain(decision: Decision, pct: float | None) -> dict:
    """Render local English and Kannada verdict templates."""
    templates = {
        'FIXED': ('Repair verified. {pct}% of the original pothole has been fixed.',
                  'ದುರಸ್ತಿ ಪೂರ್ಣಗೊಂಡಿದೆ. ಮೂಲ ಗುಂಡಿಯ {pct}% ಭಾಗ ಸರಿಪಡಿಸಲಾಗಿದೆ.'),
        'PARTIAL': ('Partial repair. Only {pct}% of the original pothole has been fixed. Re-inspection needed.',
                    'ಭಾಗಶಃ ದುರಸ್ತಿ. ಮೂಲ ಗುಂಡಿಯ {pct}% ಭಾಗ ಮಾತ್ರ ಸರಿಪಡಿಸಲಾಗಿದೆ. ಮರುಪರಿಶೀಲನೆ ಅಗತ್ಯ.'),
        'NOT_FIXED': ('Not repaired. The pothole is still there.', 'ದುರಸ್ತಿ ಆಗಿಲ್ಲ. ಗುಂಡಿ ಇನ್ನೂ ಹಾಗೆಯೇ ಇದೆ.'),
        'NEEDS_REVIEW': ('Could not verify automatically. An official needs to check this.',
                         'ಸ್ವಯಂ ಪರಿಶೀಲನೆ ಸಾಧ್ಯವಾಗಿಲ್ಲ. ಅಧಿಕಾರಿಯಿಂದ ಪರಿಶೀಲನೆ ಅಗತ್ಯ.'),
        'SUSPICIOUS': ('Suspicious photo: the after photo appears to be from a different location.',
                       "ಸಂಶಯಾಸ್ಪದ ಫೋಟೋ: 'ನಂತರ'ದ ಫೋಟೋ ಬೇರೆ ಸ್ಥಳದಿಂದ ತೆಗೆದಂತೆ ಕಾಣುತ್ತದೆ."),
    }
    en, kn = templates[decision.verdict]
    if decision.verdict == 'SUSPICIOUS' and any(
        word in reason.lower() for reason in decision.reasons for word in ('duplicate', 'another complaint')
    ):
        en = 'Suspicious photo: this same photo was used for another complaint.'
        kn = 'ಸಂಶಯಾಸ್ಪದ ಫೋಟೋ: ಇದೇ ಫೋಟೋವನ್ನು ಬೇರೆ ದೂರಿಗೂ ಬಳಸಲಾಗಿದೆ.'
    value = f'{pct:g}' if pct is not None else 'unknown'
    return {'en': en.format(pct=value), 'kn': kn.format(pct=value)}
