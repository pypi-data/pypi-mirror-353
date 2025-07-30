env_init
menu_init

default='lg'

menuentry 'bash / latest / gui' --id 'lg' { debsquash '/w/boot/bash/latest/gui' }
menuentry 'bash / latest / tui' --id 'lt' { debsquash '/w/boot/bash/latest/tui' }
menu_split
menuentry 'bash / stable / gui' --id 'sg' { debsquash '/w/boot/bash/stable/gui' }
menuentry 'bash / stable / tui' --id 'st' { debsquash '/w/boot/bash/stable/tui' }
menu_split
menuentry 'ubuntu / latest' { ubusquash '/w/boot/ubuntu/latest' }
menuentry 'ubuntu / stable' { ubusquash '/w/boot/ubuntu/stable' }
menu_split
menuentry 'alma / latest' { almsquash '/w/boot/alma/latest' }
menuentry 'alma / stable' { almsquash '/w/boot/alma/stable' }
menu_split
menuentry 'work / tui / stable' { debsquash '/w/boot/work/tui.stable' }
menuentry 'work / tui / latest' { debsquash '/w/boot/work/tui.latest' }
menu_split
menuentry 'work / gui / stable' { debsquash '/w/boot/work/gui.stable' }
menuentry 'work / gui / latest' { debsquash '/w/boot/work/gui.latest' }
