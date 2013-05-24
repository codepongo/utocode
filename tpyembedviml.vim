if !has('python')
	echo 'error'
endif

python << EOF

print 'hi, python + vimL'

EOF
