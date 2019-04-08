module.exports = function(grunt) {

    // Configuration
    grunt.initConfig({
	pkg: grunt.file.readJSON('package.json')
	, sass: {
	    dist: {
		options: {
		    style: 'compact'
		},
		files: {
		    '../static/css/style.css': '../static/scss/style.scss',
		    '../static/css/error.css': '../static/scss/errors.scss'
		}
	    }
	}
	, postcss: {
	    options: {
		//diff: true,
		//map: true, // inline sourcemaps
		// or
		map: {
		    //inline: false, // save all sourcemaps as separate files...
		    annotation: '../static/css/maps/' // ...to the specified directory
		}
		
		, processors: [
		    require('pixrem')(), // add fallbacks for rem units
		    require('autoprefixer')({browsers: 'last 2 versions'}), // add vendor prefixes
		    require('cssnano')() // minify the result
		]
	    }
	    , dist: {
		src: '../static/css/*.css'
	    }
	}
	, watch: {
	    options: {
        	livereload: true,
    	    },
	    css: {
		files: ['../static/scss/**/*.scss'],
		tasks: ['sass','postcss'],
		options: {}
	    }
	}
    });


    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-postcss');

    // Start
    grunt.registerTask('default', ['sass', 'postcss', 'watch']);

};
