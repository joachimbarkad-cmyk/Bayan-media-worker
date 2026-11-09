"""Formes de dictionnaire imposées quand l'extraction automatique (orthographe
uthmanie, variantes de lecture, confusions de lemme) donnerait une forme peu
lisible ou contestable."""

# inaccompli (3e m. sg.) à afficher pour ces verbes
IMPF = {
    'قَرَأَ': 'يَقْرَأُ',
    'سَأَلَ': 'يَسْأَلُ',
    'اهْتَدَى': 'يَهْتَدِي',
    'أَغْنَى': 'يُغْنِي',
    'أَغْنَتْ': 'يُغْنِي',
    'تَذَكَّرَ': 'يَتَذَكَّرُ',
    'تَزَكَّى': 'يَتَزَكَّى',
    'طَغَى': 'يَطْغَى',
    'تَلَى': 'يَتْلُو',
    'دَعا': 'يَدْعُو',
    'عَفا': 'يَعْفُو',
    'أَتَى': 'يَأْتِي',
    'كِيدُ': 'يَكِيدُ',
    'بَنَى': 'يَبْنِي',
}

# pas de pluriel affiché (lemme ambigu dans le corpus, ou pluriel rare)
NO_PLURAL = set('عَلِيم إِنسان بُنَىّ بُنَيّ دُعاء صالِح ظَنّ قُوَّة أَهْل نِساء'.split())

# pluriels imposés
PLURAL = {
    'ابْن': 'أَبْنَاء',
    'يَد': 'أَيْدٍ',
    'وَلِيّ': 'أَوْلِيَاء',
    'نَبَأ': 'أَنْبَاء',
    'لِسان': 'أَلْسِنَة',
    'مَتاع': 'أَمْتِعَة',
}
