    //
//  rootViewController.m
//  say
//
//  Created by zuohaitao on 12-1-9.
//  Copyright 2012 zuohaitao@doaob. All rights reserved.
//

#import "rootViewController.h"


@implementation rootViewController

@synthesize birthday;
@synthesize note;
@synthesize say;

// The designated initializer.  Override if you create the controller programmatically and want to perform customization that is not appropriate for viewDidLoad.
/*
- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization.
    }
    return self;
}
*/

/*
// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)loadView {
}
*/


// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad {
	sayViewController* sayController = [[sayViewController alloc]
												  initWithNibName:@"sayViewController" bundle:nil];
	self.say = sayController;
	[self.view insertSubview:sayController.view atIndex:0];
	[sayController release];
    [super viewDidLoad];
}


/*
// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    // Return YES for supported orientations.
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}
*/

- (void)didReceiveMemoryWarning {
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc. that aren't in use.
	if (self.say.view.superview == nil) {
		self.say = nil;
	}
	else if (self.birthday.view.superview == nil) {
		self.birthday = nil;
	}
	else if (self.note.view.superview == nil) {
		self.note = nil;
	}
	else {
	}
}

- (void)viewDidUnload {
	NSLog(@"%s", __FUNCTION__);
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}


- (void)dealloc {
	[birthday release];
	[note release];
    [super dealloc];
}

- (IBAction)switchViews:(id)sender
{
	NSLog(@"%s", __FUNCTION__);
	
	[UIView beginAnimations:@"View Flip" context:nil];
	[UIView setAnimationDuration:1.25];
	[UIView setAnimationCurve:UIViewAnimationCurveEaseInOut];
	
	if (self.say.view.superview != nil) {
		if (self.birthday == nil) {
			birthdayViewController* birthdayController = [[birthdayViewController alloc]
														  initWithNibName:@"birthdayViewController" bundle:nil];
			self.birthday = birthdayController;
			[birthdayController release];
		}
		
		[UIView setAnimationTransition:
		 UIViewAnimationTransitionFlipFromRight forView:self.view cache:YES];
		[birthday viewWillAppear:YES];
		[say viewWillDisappear:YES];
		
		[say.view removeFromSuperview];
		[self.view insertSubview:birthday.view atIndex:0];
		
		[say viewWillAppear:YES];
		[birthday viewWillDisappear:YES];
		[UIView commitAnimations];
		
		
	}
	else if (self.birthday.view.superview != nil) {
		if (self.note == nil) {
			noteViewController* noteController = [[noteViewController alloc]
												  initWithNibName:@"noteViewController" bundle:nil];
			self.note = noteController;
			[noteController release];
		}
		[birthday.view removeFromSuperview];
		[self.view insertSubview:note.view atIndex:0];
		
	}
	else if (self.note.view.superview != nil) {
		if (self.say == nil) {
			sayViewController* sayController = [[sayViewController alloc]
												  initWithNibName:@"sayViewController" bundle:nil];
			self.say = sayController;
			[sayController release];
		}
		[note.view removeFromSuperview];
		[self.view insertSubview:say.view atIndex:0];
	}
	else {
	}
}
@end
