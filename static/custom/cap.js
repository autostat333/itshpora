
// CAPSULEFOR <angularjs_frame;OPEN>
app = angular.module("app",['ui.router','ui.bootstrap','ngCookies']);





app.config(function($stateProvider, $urlRouterProvider)
	{
	$urlRouterProvider.otherwise('/notes')
	$stateProvider
		.state('notes',
			{
			templateUrl:"./static/tmp/notes.html",
			controller:"NotesController",
			url:"/notes"
			})
		.state('login',
			{
			templateUrl:"./static/tmp/login.html",
			controller:"LoginController",
			url:"/login"
			})
		.state('contact',
			{
			templateUrl:'./static/tmp/contact.html',
			controller:'ContactController',
			url:'/contact'
			})


	})


app.controller("MainController",function($scope,$http,$state,$cookies,$modal,$location)
	{
	//redirect to sign page, uf user is unsigned
	if ($cookies.get('log_token')==undefined)
		{
		window.location.replace('#/login');
		}

	//////////////////////////////////////////////
	//////CHECK PERMISSION BLOCK//////////////////


	$scope.CURRENT_USER = false;
	$scope.check_user = function()
		{
		$http.get('./user').then(function(res)
			{
			if (res.data.indexOf('Error User')==0)
				{
				$scope.CURRENT_USER = false;
				}
			else
				{
				$scope.CURRENT_USER = res.data;
				}
			$scope.CURRENT_USER = res.data.indexOf('Error User')==0?false:res.data;
			},function(err)
			{
			alert('Error obtainig data from server')
			})
		}
	$scope.check_user();


	$scope.logout_preloader = false;
	$scope.logout = function()
		{
		$scope.logout_preloader = true;
		$http.get('./drop').then(function()
			{
			window.location.reload();
			},function(err)
			{
			alert(err.res);
			$scope.logout_preloader = true;
			})

		}
	//////END CHECK PERMISSION BLOCK//////////////////
	//////////////////////////////////////////////////

	$scope.login_preloader = false;
	$scope.show_alert = false;
	$scope.login = function()
		{
		$scope.login_preloader = true;
		$scope.show_alert = false;


		if ($scope.u_name==''||$scope.u_pass=='')
			{
			$scope.show_alert = 'not allowed empty fields';
			$scope.login_preloader = false;
			return false;
			}

		var d = {};
		d['name'] = $scope.u_name;
		d['pass'] = $scope.u_pass;
		$scope.u_name = '';
		$scope.u_pass = '';		

		$http.post('./login',d).then(function(res)
			{
			var tmp = res.data;
			if (tmp!='Logged')
				{
				$scope.login_preloader = false;
				$scope.show_alert = tmp.split(':')[1];  //show logging alert
				}
			else
				{
				window.location.reload();
				}
			},function(err)
				{
				$scope.show_alert = 'Probably Server not responding! Try later!';
				$scope.server_alert = true;
				$scope.login_preloader = false;
				});
				
		}
	$scope.close_alert = function()
		{
		$scope.show_alert = false;
		$scope.u_pass='';	
		}



	$scope.question = function()
		{

		$modal.open(
			{
			templateUrl:'./static/tmp/modal_question.html',
			controller:"ModalQuestionController",
			scope:$scope
			})		

		}


	$scope.hide_menu = function(path)
		{
		if (path===$location.$$path){return false}
		$('.navbar-collapse').collapse('hide');
	//	$('.first_preloader').css('display','block');
		$('.first_preloader').removeClass('hide_preloader');
		
		}


	})



app.controller('NotesController',function($scope,$http,$modal)
	{
	$scope.nav_state = 'quick_add';
	//block to check permission
	$http.get('./user').then(function(res)
		{
		if (res.data.indexOf('Error User')==0)
			{
			$scope.CURRENT_USER = false;
			}
		else
			{
			$scope.CURRENT_USER = res.data;
			}
		$scope.CURRENT_USER = res.data.indexOf('Error User')==0?false:res.data;
		},function(err)
		{
		alert('Error obtainig data from server')
		})

	//for searh
	$scope.query = '';

	$scope.$watch('query',function()
		{
		$scope.search_loading = false;
		$scope.search_results = [];
	
		if ($scope.query!="")
			{
			d = {};
			d['query'] = $scope.query;
			$scope.nav_state = 'search';
			$http.post('./notes/search',d).then(function(res)
				{
				if (res.data.toString().search('Error')==0)	
					{
					$scope.show_alert = 'Error occurs on the server side.';
					}
				else
					{
					$scope.search_results = res.data;	
					}

				},function(err)
					{
					$scope.show_alert = 'Problems with connection or with server! Try later!';
					console.log(err.data);
					})
			}
	
			
//		else   //for auto switch to agenda if query is deleted
//			{
//			$scope.nav_state = 'agenda';
//			}

		})


	$scope.mobile_show = mobile_show;


	function mobile_show()
		{
		var el = $('.switch_container');
		if (!el.hasClass('open'))
			el.addClass('open');	
		else
			el.removeClass('open');

		}

	})



app.controller('AgendaController',function($scope,$http,$modal)
	{


	//////////////////////////////////////////////////////
	////////////////////AGENDA////////////////////////////
	//////////////////////////////////////////////////////

	$scope.section_name = ''; //it is object with 'id' and 'name' keys
	$scope.sections = [];
	$scope.section_loading = false;  //for spinner during section list loading
	$scope.show_box_btn = {};  //it is dictionarry for hover flags (hover of code notes items)
	//GET SECTION LIST
	$scope.get_sections = function()
		{
		$scope.section_loading = true;
		$http.get('./section/list').then(function(res)
			{
			$scope.section_loading = false;
			$scope.sections = res.data;
			console.log($scope.sections);
			//refresh section name
			$scope.section_name = $scope.section_name==''?(res.data.length==0?'':res.data[0]):$scope.section_name;
			},function(err)
			{
			alert('Problems with connection or with server. Try later please!');
			console.log(err.data)
			})

		}
	

	//GET NOTES
	$scope.$watch('section_name',function(old_value,new_value)
		{
		$scope.notes = [];
		console.log('sec_name:'+$scope.section_name);
		if ($scope.section_name==undefined){return false};
		if ($scope.section_name['id']==''){return false};
		$scope.get_notes();

		},true);



	//GET NOTES FOR SELECTED SECTION	
	$scope.get_notes = function()
		{
		if ($scope.section_name==''){return false};
		$http.get('./section/'+$scope.section_name['id']+'/notes').then(function(res)
			{
			if (res.data.toString().search('Error')!=0)
				{
				$scope.notes = res.data;
				}
			else
				{
				$scope.notes = [];
				}

			},function(err)
			{
			alert('Problems with connection or with server. Try later please!');
			})


		}

	

	$scope.get_sections(); //initialize sections
	$scope.get_notes();

	//ADD SECTION
	$scope.add_section = function()
		{

		$modal.open(
			{
			templateUrl: './static/tmp/modal_add_section.html',
			controller: 'ModalAddSectionController',
			scope: $scope
			})
		}

	//ADD NOTES in CURRENT SECTION
	$scope.add_notes = function()
		{
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_add_notes.html',
			controller:'ModalAddNotesController',
			scope:$scope
			})		

		}	

	//BOX BUTTONS
	$scope.dispatch_note = function(it)
		{
		$scope.clicked_note = it;
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_dispatch_note.html',
			controller:'ModalDispatchNoteController',
			scope:$scope
			})		

		}	
	$scope.edit_note = function(it)
		{
		$scope.clicked_note = it;
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_edit_note.html',
			controller:'ModalEditNoteController',
			scope:$scope
			})		

		}	
	$scope.remove_note = function(it)
		{
		$scope.clicked_note = it;
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_remove_note.html',
			controller:'ModalRemoveNoteController',
			scope:$scope
			})		

		}	

	//SECTIONS CONTROLS
	$scope.rename_section = function()
		{
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_rename_section.html',
			controller:'ModalRenameSectionController',
			scope:$scope
			})		
	
	
		}	
	
	$scope.merge_section = function()
		{
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_merge_section.html',
			controller:'ModalMergeSectionController',
			scope:$scope
			})		
	
	
		}	
	$scope.remove_section = function()
		{
		$modal.open(
			{
			templateUrl:'./static/tmp/modal_remove_section.html',
			controller:'ModalRemoveSectionController',
			scope:$scope
			})		
	
	
		}	


	})


app.controller('SearchController',function($scope,$http)
	{


	})




app.controller('QuickAddController',function($scope,$http)
	{
	$scope.section_name = '';
	$scope.comment = '';
	$scope.code_note = '';	
	$scope.sections = [{'name':'Wait for loading......','id':'1'}];
	$scope.show_alert = false;
	$scope.loading = false;

	$scope.show_success = false;
	
	//get list of sectionns just tab is active
	$scope.get_sections = function()
		{
		$scope.show_alert = false;
		$http.get('./section/list').then(function(res)
			{
			$scope.sections = res.data;
			console.log('sections');
			//refresh section name
			},function(err)
			{
			alert('Problems with connection or with server. Try later please!');
			console.log(err.data)
			})

		}
	$scope.get_sections();



	//SUBMITTING
	$scope.submit_btn = function()
		{
		$scope.show_alert = false;
		$scope.show_success = false;

		//simple validation
		if ($scope.comment==''||$scope.code_note==''||$scope.section_name=='')
			{
			$scope.show_alert = 'One filed is empty. Please, complete it!';
			return false;
			}	

		if ($scope.section_name=='Wait for loading......')
			{
			$scope.show_alert = 'List with sections have not loaded. Please wait!';
			return false;
			}

		$scope.loading = true;
		d = {};
		d['section'] = $scope.section_name;
		d['comment'] = $scope.comment;
		d['code_note'] = $scope.code_note;
		$http.post('./notes/add',d).then(function(res)
			{
			$scope.loading = false;
			if (res.data.search('Error')==0)
				{
				$scope.show_alert = res.data;
				
				}
			else
				{
				$scope.show_success = 'Code Notes has been added! Thanks!';	
				$scope.code_note = '';
				$scope.comment = '';
				}

			},function(err)
			{
			$scope.show_alert = 'Some problems with server. Please, try later!';
			console.log(err.data);
			$scope.loading = false;
	
			})
		}	



	
	

	function get_id_section(section_name)
		{
		var l = $scope.sections.length;
		for (var i=0;i<l;i=i+1)
			{
			if (section_name==$scope.sections[i]['name'])
				{
				return $scope.sections[i]['id'];
				}
			}	

		
		}



	})


//////////////////////////////////////////////////////////////////
////////////////CONTROLLERS FOR MODAL WINDOWS/////////////////////
//////////////////////////////////////////////////////////////////



app.controller('ModalQuestionController',function($scope,$uibModalInstance)
	{
	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}
	

	})





app.controller('ModalRenameSectionController',function($scope,$http,$uibModalInstance)
	{
	$scope.loading = false;
	$scope.show_alert = false;
	$scope.new_section_name = $scope.section_name['name'];

	//autofocus
	setTimeout(function(){$('.modal input').focus()},500);
	$scope.submit_modal = function()
		{
	
		_id = $scope.section_name['id'];
		d = {};
		d['_id'] = _id;
		d['new_name'] = $scope.new_section_name;
		
		//simple validation
		console.log($scope.new_section_name);
		if ($scope.new_section_name=='')
			{
			$scope.show_alert='Empty field is not allowed. Please, input something!';
			return false;
			}



		$scope.loading = true;   //switch on preloader
		$http.post('./section/rename',d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				
				}
			else
				{
				$uibModalInstance.close();
				$scope.$parent.section_name = '';
				$scope.get_sections();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}

		
	});


app.controller('ModalMergeSectionController',function($scope,$http,$uibModalInstance)
	{

	$scope.loading = false;
	$scope.show_alert = false;
	$scope.new_section_name = '';
	$scope.submit_modal = function()
		{
	
		_id = $scope.section_name['id'];
		d = {};
		d['_id_from'] = _id;
		d['_id_where'] = get_id_section($scope.new_section_name)

		if ($scope.new_section_name=='')
			{
			$scope.show_alert='Empty field is not allowed. Please, choose something!';
			return false;
			}

		$scope.loading = true;   //switch on preloader
		$http.post('./section/merge',d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				
				}
			else
				{
				$uibModalInstance.close();
				$scope.$parent.section_name = '';
				$scope.get_sections();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		}

	function get_id_section(section_name)
		{
		var l = $scope.sections.length;
		for (var i=0;i<l;i=i+1)
			{
			if (section_name==$scope.sections[i]['name'])
				{
				return $scope.sections[i]['id'];
				}
			}	

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}



	
	});


app.controller('ModalRemoveSectionController',function($scope,$http,$uibModalInstance)
	{
	$scope.show_alert = false;
	$scope.loading = false;
	$scope.submit_modal = function()
		{
	
		d = {};
		_id = $scope.section_name['id'];
		d['_id'] = _id;
		$scope.loading = true;   //switch on preloader
		$http.post('./section/remove',d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				
				}
			else
				{
				$uibModalInstance.close();
				$scope.$parent.section_name = '';
				$scope.get_sections();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}



	});


app.controller('ModalDispatchNoteController', function($scope,$http,$uibModalInstance)
	{
	$scope.show_alert = false;
	$scope.target_section = '';
	$scope.loading = false;

	$scope.submit_modal = function()
		{
		if ($scope.target_section=='')
			{
			$scope.show_alert = ' you need choose some section.';
			return false;
			}
	
		d = {};
		d['id_note'] = $scope.clicked_note['_id'];
		d['id_section'] = get_id_section($scope.target_section);
		$scope.loading = true;   //switch on preloader
		$http.post('./notes/dispatch',d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				
				}
			else
				{
				$uibModalInstance.close();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}

	function get_id_section(_id)
		{
		var l = $scope.sections.length;
		for (var i=0;i<l;i=i+1)
			{
			if (_id==$scope.sections[i]['name'])
				{
				return $scope.sections[i]['id'];
				}
			}	

		}


	})


app.controller('ModalEditNoteController', function($scope,$http,$uibModalInstance)
	{

	$scope.show_alert = false;
	$scope.code_note = $scope.clicked_note['_source']['code_note'];
	$scope.comment = $scope.clicked_note['_source']['comment'];
	$scope.loading = false;

	setTimeout(function(){$('.modal textarea')[0].focus()},500);

	$scope.submit_modal = function()
		{
		if ($scope.comment==''||$scope.code_note=='')
			{
			$scope.show_alert = ' one field is empty, please - complete it!';
			return false;
			}
	
		d = {};
		_id = $scope.clicked_note['_id'];
		d['code_note'] = $scope.code_note;
		d['comment'] = $scope.comment;
		$scope.loading = true;   //switch on preloader
		$http.post('./notes/update/'+_id,d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				
				}
			else
				{
				$uibModalInstance.close();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}



	})


app.controller('ModalRemoveNoteController', function($scope,$http,$uibModalInstance)
	{
	$scope.loading = false;
	$scope.show_alert = false;
	
	$scope.submit_modal = function()
		{
	
		_id = $scope.clicked_note['_id'];
		$scope.loading = true;   //switch on preloader
		$http.get('./notes/remove/'+_id).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				$scope.section_name = '';				
				$scope.get_sections();
				}
			else
				{
				$uibModalInstance.close();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}



	})



app.controller('ModalAddSectionController', function($scope,$http,$uibModalInstance)
	{
	$scope.new_section_name = '';
	$scope.loading = false;
	$scope.show_alert = false;

	setTimeout(function(){$('.modal input').focus()},500);

	$scope.submit_modal = function()
		{
		d = {};
		d['name'] = $scope.new_section_name;
		$scope.loading = true;   //switch on preloader
		$http.post('./section/add',d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				}
			else
				{
				$uibModalInstance.close();
				$scope.get_sections();
				}

			},function(err)
			{
			alert('Error connections of Server problems');

			})

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}


	})

app.controller('ModalAddNotesController', function($scope,$http,$uibModalInstance)
	{
	$scope.code_note = '';
	$scope.comment = '';
	$scope.show_alert = false;

	$scope.loading = false;

	setTimeout(function(){$('.modal textarea')[0].focus()},500);


	$scope.submit_modal = function()
		{
		d = {};
		d['section'] = $scope.section_name['name'];
		d['code_note'] = $scope.code_note;
		d['comment'] = $scope.comment;



		if ($scope.code_note==''||$scope.comment=='')
			{
			$scope.show_alert = 'Empty fileds is not allowed, please - complete.';
			return false;
			}

		$scope.loading = true;   //switch on preloader
		$http.post('./notes/add',d).then(function(res)
			{
			$scope.loading = false;  //switch off lpreloader
			if (res.data!='OK')
				{
				$scope.show_alert = res.data;
				}
			else
				{
				$uibModalInstance.close();
				$scope.get_notes();
				}

			},function(err)
			{
			alert('Error connections of Server problems');
			})

		
		}


	$scope.close_modal = function()
		{
		$uibModalInstance.close();
		}
	})






app.controller('LoginController',function($scope,$http)
	{
	//block to check permission
	$scope.check_permission = function()
		{
		$http.get('./user').then(function(res)
			{
			if (res.data.indexOf('Error User')==0)
				{
				$scope.CURRENT_USER = false;
				}
			else
				{
				$scope.CURRENT_USER = res.data;
				}
			$scope.CURRENT_USER = res.data.indexOf('Error User')==0?false:res.data;
			},function(err)
			{
			alert('Error obtainig data from server')
			})
		}

	$scope.check_permission();

	$scope.$watch('$parent.CURRENT_USER',function()
		{
		$scope.check_permission();

		})

	

	})


app.controller('ContactController',function($scope,$http)
	{
	$scope.show_alert = false;
	$scope.show_success = false;

	$scope.email = '';
	$scope.text = '';	
	$scope.loading = false;

	$scope.submit = function()
		{
		if ($scope.text==''||$scope.email=='')
			{
			$scope.show_alert='empty fields not allowed! Please, complete one!';
			return false;
			}
		d = {};
		d['email'] = $scope.email; 
		d['text'] = $scope.text;

		$scope.loading = true;
		$http.post('./feedback',d).then(function(res)
			{
			if (res.data!='OK')
				{
				$scope.loading = false;
				$scope.show_alert = 'Message has not send! Try Later!';
				} 
			else
				{
				$scope.loading = false;
				$scope.email = '';
				$scope.text = '';
				$scope.show_success = 'your message has been sent!';

				}			

			})


		};


	})









app.directive('loginRegistr',function($http,$state)
	{
	return {
		link: function(scope,element,attrs)
			{
			//set class
			scope.set_class = function()
				{
			

				if (scope.nav_state=='login')
					{
					element.css('width','300px');
					element.css('padding','30px 30px 30px 30px');
					element.css('border-radius','5px');
					element.css('background','white');
					element.css('margin','30px auto 0px auto');
					}

				if (scope.nav_state=='signin')
					{
					console.log('ffff');
					element.css('width','400px');
				//	element.css('padding','30px 30px 30px 30px');
				//	element.css('border-radius','5px');
				//	element.css('background','white');
					element.css('margin','30px auto 0px auto');
					}

				}

				scope.nav_state = 'signin';
				scope.login_preloader = false;
				scope.set_class();
				scope.show_alert = false;  //for show alert
				scope.server_alert = false; //flag for red plaha
				scope.CURRENT_USER = false;  //not logged user

				scope.u_name = '';
				scope.u_pass = '';
				scope.confirm_pass = '';	
	
				scope.goto_sign_in = function()
					{
					scope.nav_state = 'signin';
					scope.set_class();
					scope.login_preloader = false;
					scope.show_alert = false;
					scope.server_alert = false;
					}

				scope.log_in = function()
					{
					scope.login_preloader = true;
					scope.show_alert = false;
					scope.server_alert = false;		


					var d = {};
					d['name'] = scope.u_name;
					d['pass'] = scope.u_pass;
					
					$http.post('./login',d).then(function(res)
						{
						scope.login_preloader = false;  //stop preloader
						var tmp = res.data;
						if (tmp!='Logged')
							{
							scope.show_alert = tmp.split(':')[1];  //show logging alert
							}
						else
							{
							$state.go('notes');
							}
						},function(err)
						{
						scope.show_alert = 'Probably Server not responding! Try later!';
						scope.server_alert = true;
						scope.login_preloader = false;
						})
				
					}

				scope.sign_in = function()
					{

					scope.login_preloader = true;
					scope.show_alert = false;
					scope.server_alert = false;		


					//client-side validation
					if (scope.u_pass==''||scope.u_confirm_pass==''||scope.u_name=='')
						{
						scope.show_alert = 'One filed is empty!Please, complete it.'
						scope.login_preloader = false;
						return false;
						} 



					if (scope.u_pass!=scope.u_confirm_pass)
						{
						scope.show_alert = 'Passwords are different!';
						scope.login_preloader = false;
						return false;
						}


					var d = {};
					d['name'] = scope.u_name;
					d['pass'] = scope.u_pass;
					$http.post('./registr',d).then(function(res)
						{
						scope.login_preloader = false;  //stop preloader
						var tmp = res.data;
						if (tmp!='Registred')
							{
							scope.show_alert = tmp.split(':')[1];  //show logging alert
							}
						else
							{
							scope.CURRENT_USER = scope.u_name;
							window.location.reload();
							}
						},function(err)
						{
						scope.show_alert = 'Probably Server not responding! Try later!';
						scope.server_alert = true;
						scope.login_preloader = false;
						})
				
					}



				scope.close_alert = function()
					{
					scope.show_alert = false;	
					scope.server_alert = false;
					}

			},

		template: function()
			{
			/*`
		<div ng-switch on="nav_state">
			<div class="img_container">
				<img src="./static/img/bg.jpg" class="bg_img_" crop-img="viewport">
			</div>
			<form ng-switch-when="login">
				<h2 class="form-signin-heading">Please Log in</h2>
				<br>
				<input class="form-control" type="text" ng-model="$parent.u_name" class="input-block-level" placeholder="Email address">
				<br>
				<input class="form-control" type="password" ng-model="$parent.u_pass"  class="input-block-level" placeholder="Password">
			<br>	
				<div ng-if="show_alert!=false" class="alert alert-warning" ng-class="{'alert-danger':$parent.server_alert}">
					<button type="button" class="close" ng-click="close_alert()">×</button>
					<strong>Sorry,</strong> {{$parent.show_alert}}
				</div>
				<button class="btn btn-large btn-primary" ng-click="log_in()" type="submit">Log in</button>
				<button class="btn btn-large btn-link" ng-click="goto_sign_in()" type="submit">Create account</button>
			<br>
	<br><div ng-show="login_preloader"><img src="data:image/gif;base64,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"></img></div>

			</form>
	






			<form ng-switch-when="signin" class="bs-docs-example form-horizontal">
				<h2 class="form-signin-heading">Sign Up</h2>
				<hr class="bs-docs-separator"></hr>

				<label>Input you email address</label>
				<input type="text" class="form-control" ng-model="$parent.u_name" class="input-block-level" placeholder="You email address">
			<br>	<label>Password</label>
				<input ng-model="$parent.u_pass" class="form-control" type="password"  class="input-block-level" placeholder="Enter password">
			<br>	<label>Confirm Password</label>
				<input type="password" class="form-control"  ng-model="$parent.u_confirm_pass" class="input-block-level" placeholder="Confirm password">
			<br>    <div ng-if="show_alert!=false" class="alert alert-warning" ng-class="{'alert-danger':$parent.server_alert}">
 
					<button type="button" class="close" ng-click="close_alert()">×</button>
					<strong>Sorry,</strong> {{$parent.show_alert}}
				</div>

			<a role="button" class="btn btn-large btn-block btn-primary" type="submit" ng-click="sign_in()">Sign in</a>
			<br>	<img ng-show="login_preloader" src="data:image/gif;base64,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"></img>
            
			</form>


			`*/	
			}.toString().split('/*`')[1].split('`*/')[0]

		


		}

		
	


	})






app.directive('cropImg',function($timeout)
	{
	return {
		//scope:{},
		link:function(scope,element,attr)
			{
			scope.get_dimensions = get_dimensions;
			scope.resize = resize;


			var viewport = attr['cropImg']===''?false:true;

			function resize()
				{
				$timeout(scope.get_dimensions,0);
				}
			//$(window).on('resize',scope.resize);
			element.on('load',scope.get_dimensions);
			//scope.get_dimensions();	
			function get_dimensions()
				{
				var parent_element = element.parent();
				//!!! not conventional case - for safe case get transform property, cache it, remove, and return after all dimensions will be ready
				var cache_transform_parent = parent_element.css('transform');
				parent_element.css(
					{
					'transform':'',
					'visibility':'hidden'
					});


				var cache_transform_element = element.css('transform');
				element.css(
						{
						'transform':'',
						'visibility':'hidden'
						});
				if (viewport==false)
					{
					var parent_dimensions = parent_element[0].getBoundingClientRect();
					var h = parent_dimensions['height'];
					var w = parent_dimensions['width'];
					}
				else
					{
					var h = window.innerHeight;
					var w = window.innerWidth;
					}
				
				var img_dimensions = element[0].getBoundingClientRect();
				var h_img = img_dimensions['height'];
				var w_img = img_dimensions['width'];
				var koef = w/w_img;
				//debugger;
				if (h_img*koef>=h)
					{
					element.css(
						{
						'width':w+'px',
						'height':'auto',
						'margin-left':'0%'
						});
					//element.css({'width':'100%','height':'auto'});
					}
				else
					{
					var new_w_img = w_img*(h/h_img);
					var rate = (1-new_w_img/w)/2*100;
					//debugger;
					element.css(
						{
						'width':'auto',
						'height':h+'px',
						'margin-left':rate+'%'
						});
					}
				//console.log(h,w,h_img,w_img,rate,new_w_img);
				//return previous state (transforms and visibility)
				parent_element.css(
					{
					'transform':cache_transform_parent,
					'visibility':'visible'
					});
				element.css(
						{
						'transform':cache_transform_element,
						'visibility':'visible'
						});

				$('.first_preloader').addClass('hide_preloader');


				//debugger;
				}

			}
	

	}


	})




app.directive('animateScroll',function($window)
	{
	return {
		scope:{},
		link: function(scope,element,attrs)
			{

			scope.init = init;
			scope.getDimensions = getDimensions;
			var el = element[0];
			var when_scroll = attrs['whenScroll']===undefined?undefined:parseInt(attrs['whenScroll'])/100;

			scope.init();

			function getDimensions()
				{
				scope.elemTopPos = element[0].getBoundingClientRect()['top'];
				scope.viewportHeight = $window.innerHeight;
				}

			function init()
				{
				scope.getDimensions();
		//		el.style['opacity'] = '0';
				scope.finished = false; //animation is finished (prevent scrol handling)
				}

			
		
			//determine when to fire animation
			$(window).scroll(function()
				{
				if (scope.finished==true){return false;}
		
				var scroll_top = $(window).scrollTop();
				var koef = scroll_top/scope.viewportHeight;
				if (when_scroll!=undefined)
					{
					if (koef>when_scroll)
						{
					//	if (attrs['animateScroll']=='reduce'){debugger;}
						$(el).addClass(attrs['animateScroll']); //set animated class
						scope.finished = true;
						scope.$apply();
					//	if (attrs['animateScroll']=='reduce'){debugger;}
						
						}
					return false
					}

				var dist = -scroll_top + scope.elemTopPos;
				if (dist/scope.viewportHeight<0.7)
					{
					$(el).addClass(attrs['animateScroll']); //set animated class
					scope.finished = true;
					scope.$apply();
					}		
				})

				

			}
		

		}


	})




app.directive('scrollUp',function()
	{

	return {

	link:function(scope,element)
		{
		var scroll_pos = $('body').scrollTop();
		//var flag = false;

		function show_hide()
			{

			if (scroll_pos>50&&!element.hasClass('show'))
				{element.addClass('show');flag = true}
			if (scroll_pos<50&&element.hasClass('show'))
				{element.removeClass('show');}
				
			}
		show_hide();

		console.log(scroll_pos);
		element.on('click',function()
			{
			$('body').animate({'scrollTop':'0px'});
			})


		$(window).scroll(function()
			{
			//if (flag==true){return false};
			scroll_pos = $('body').scrollTop();
			show_hide();
			})

		}

	}

	})


app.directive('highlight',function($timeout)
	{
	return {
	link:function(scope,element)
		{
		$timeout(function()
			{
			hljs.highlightBlock(element[0]);
			})
		}

	}


	})



app.directive('setHeight',function()
	{
	return {
		compile:function()
			{
			return {
			pre:function(scope,element,attrs)
				{
		
				//append new div to retrive precise dimensions of viewport

				scope.set_height = set_height;
			
				function set_height()
					{
					var block = $('.for_viewport_dim');
					if (block.length==0)
						{
						var div = $('<div></div>');
						div.addClass('for_viewport_dim');
						div.css({'width':'100%','height':'100%','display':'none'});
						$('html').append(div);
						}

					var height = attrs['setHeight'].replace('%','');
					var viewport_height = $('.for_viewport_dim').height();
					$(element).height(viewport_height*height/100);
					}
				scope.set_height();
				//$(window).on('resize',scope.set_height);

				},
			post:function()
				{


				}

			   }

			}

		}
	})

app.directive('setWidth',function()
	{
	return {

		compile:function()
			{
			return {
				pre:function(scope,element,attrs)
					{

					scope.set_width = set_width;


					function set_width()
						{
						//append new div to retrive precise dimensions of viewport
						var block = $('.for_viewport_dim');
						if (block.length==0)
							{
							var div = $('<div></div>');
							div.addClass('for_viewport_dim');
							div.css({'width':'100%','height':'100%','display':'none'});
							$('html').append(div);
							}
						var width = attrs['setWidth'].replace('%','');
						var viewport_width = $('.for_viewport_dim').width();
						$(element).width(viewport_width*width/100);
						}
					scope.set_width();
				//	$(window).on('resize',scope.set_width);

	
					},
				post:function()
					{

					}
		

			   	}

			}


		}
	})



