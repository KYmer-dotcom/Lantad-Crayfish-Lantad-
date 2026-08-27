
MANAGER_COLORS = ['blue']
COLOR_PALETTE = {
    'blue': {
        '50': '#f2fbfd',
        '100': '#d6f1f8',
        '200': '#b9e6f2',
        '400': '#79cbe3',
        '500': '#4eb5d6',
        '600': '#2e98bf',
        '700': '#1f738f',
        '800': '#195a6f',
        '900': '#10374a',
    },
    'red': {
        '50': '#fff2ed',
        '100': '#ffd9cc',
        '200': '#ffc2b1',
        '400': '#ef6a52',
        '500': '#d94a35',
        '600': '#bf3323',
        '700': '#96281b',
        '800': '#6f1d14',
        '900': '#4a120c',
    },
    'green': {
        '50': '#eef7f1',
        '100': '#d7efe0',
        '200': '#bfe4cd',
        '400': '#4aa06b',
        '500': '#2f8755',
        '600': '#226d45',
        '700': '#1a5536',
        '800': '#143f29',
        '900': '#0e291b',
    },
    'yellow': {
        '50': '#fffaf2',
        '100': '#f7ecd6',
        '200': '#f1e2bf',
        '400': '#e9d09a',
        '500': '#d9b86a',
        '600': '#bf9a49',
        '700': '#9b7b3a',
        '800': '#71572a',
        '900': '#4c3a1b',
    },
}


def theme_context(request):
    color = 'blue'
    request.session['theme_color'] = 'blue'

    palette = COLOR_PALETTE.get(color, COLOR_PALETTE['blue'])
    theme = {
        'color': color,
        'hex': palette['600'],
        'hex_dark': palette['700'],
        'color_50': palette['50'],
        'color_100': palette['100'],
        'color_200': palette['200'],
        'color_400': palette['400'],
        'color_500': palette['500'],
        'color_600': palette['600'],
        'color_700': palette['700'],
        'color_800': palette['800'],
        'color_900': palette['900'],
        'sidebar_from': f'from-{color}-600',
        'sidebar_to': f'to-{color}-500',
        'sidebar_bg': f'bg-{color}-600',
        'sidebar_border': 'border-white/20',
        'nav_active': f'bg-white text-{color}-700',
        'nav_text': 'text-white/80',
        'nav_hover': 'hover:bg-white/10',
        'avatar_bg': 'bg-white/20',
        'role_text': 'text-white/70',
        'logout_text': 'text-white/70',
    }

    return {'theme': theme}
