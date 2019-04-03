module.exports = function(grunt) {

    // Configuration
    grunt.initConfig({
	pkg: grunt.file.readJSON('package.json'),
	sass: {
	    dist: {
		options: {
		    style: 'compact'
		},
		files: {
		    '../static/css/style.css': '../static/scss/style.scss'
		}
	    }
	},
	watch: {
	    options: {
        	livereload: true,
    	    },
	    css: {
		files: ['../static/scss/**/*.scss'],
		tasks: ['sass'],
		options: {}
	    }
	}
    });


    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // Start
    grunt.registerTask('default', ['sass', 'watch']);

};
