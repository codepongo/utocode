//
//  sayViewController.m
//  say
//
//  Created by zuohaitao on 11-12-10.
//  Copyright 2011 zuohaitao@doaob. All rights reserved.
//

#import "sayViewController.h"

@implementation sayViewController

@synthesize words;
@synthesize name;
@synthesize idx;
@synthesize _button;
@synthesize _slider;
@synthesize _image;
@synthesize _landscape_left;
@synthesize _self_view;
@synthesize _landscape_left_words;

-(IBAction)say:(id)sender {
	NSLog(@"%s", __FUNCTION__);
	[self backgroundTap:sender];
	NSString* str1 = @"";
	int which = [idx.text intValue];
	switch (which) {
		case 0:
			str1 = @"I love you.";
			break;
		case 1:
			str1 = @"我爱你。";
			break;
		case 2:
			str1 = @"别闹啦!";
			break;
		case 3:
			str1 = @"小胖子";
			break;
		case 4:
			str1 = @"挠挠";
			break;
		case 5:
			str1 = @"";
			break;
		case 6:
			str1 = @"别闹啦!";
			break;
		case 7:
			str1 = @"别闹啦!";
			break;
		case 8:
			str1 = @"别闹啦!";
			break;
		case 9:
			str1 = @"别闹啦!";
			break;
		default:
			str1 = @"";
			break;
	}
	NSString* str = [NSString stringWithFormat:@"%@%@", str1, name.text];
	words.text = str;
	_landscape_left_words.text = str;
}

-(IBAction)textFieldDoneEditing:(id)sender {
	[sender resignFirstResponder];
}

-(IBAction)backgroundTap:(id)sender {
	NSLog(@"%s", __FUNCTION__);
	[name resignFirstResponder];
	[idx resignFirstResponder];
}

-(IBAction)sliderChanged:(id)sender {
	UISlider* slider = (UISlider*)sender;
	int value = ((int)(slider.value*10))%10;
	NSLog(@"%f -> %d", slider.value, value);
	NSString* newText = [[NSString alloc] initWithFormat:@"%d",value];
	idx.text = newText;
	[newText release];
	[self say:sender];
}

-(IBAction)segmentChanged:(id)sender {
	if (0 == [sender selectedSegmentIndex])
	{
		_button.hidden = NO;
		_slider.hidden = YES;
	}
	else {
		_button.hidden = YES;
		_slider.hidden = NO;
	}
}

-(IBAction)switchChanged:(id)sender {
	UISwitch* whichSwitch = (UISwitch*)sender;
	BOOL setting = whichSwitch.isOn;
	if (setting) {
		NSLog(@"%s", "YES");
		UIActionSheet* action = [[UIActionSheet alloc]
								 initWithTitle:@"Click a button"
								 delegate:self
								 cancelButtonTitle:@"Cancel"
								 destructiveButtonTitle:@"OK"
								 otherButtonTitles:nil];
		[action showInView:self.view];
		[action release];
	}
	else {
		NSLog(@"%s", "NO");
		UIAlertView* alert = [[UIAlertView alloc]
							  initWithTitle:@"NO"
							  message:@"NO is switched"
							  delegate:self
							  cancelButtonTitle:@"Close"
							  otherButtonTitles:nil];
		[alert show];
		[alert release];
		
		
	}

}

-(void)actionSheet:(UIActionSheet*)action didDismissWithButtonIndex:(NSInteger)buttonIndex {
	if (buttonIndex == [action cancelButtonIndex]) {
		UIAlertView* alert = [[UIAlertView alloc]
							  initWithTitle:@"Clicked"
							  message:@"cancel is clicked"
							  delegate:self
							  cancelButtonTitle:@"OK"
							  otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}



// Implement viewDidLoad to do additional setup after loading the view, typically from a nib.
- (void)viewDidLoad {
    [super viewDidLoad];
	NSLog(@"%s", __FUNCTION__);
	self._self_view = self.view;
}




/*
// The designated initializer. Override to perform setup that is required before the view is loaded.
- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}
*/

/*
// Implement loadView to create a view hierarchy programmatically, without using a nib.
- (void)loadView {
}
*/





// Override to allow orientations other than the default portrait orientation.
- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    // Return YES for supported orientations
    //return (interfaceOrientation == UIInterfaceOrientationPortrait);
	id msg = nil;
	switch (interfaceOrientation) {
		case UIInterfaceOrientationPortrait:
			msg = [NSString stringWithString:@"纵向OrientationPortrait"];
			break;
		case UIInterfaceOrientationPortraitUpsideDown:
			msg = [NSString stringWithString:@"纵向倒置OrientationPortraitUpsideDown"];
			break;
		case UIInterfaceOrientationLandscapeLeft:
			msg = [NSString stringWithFormat:@"横向左OrientationLandscapeLeft"];
			break;
		case UIInterfaceOrientationLandscapeRight:
			msg = [NSString stringWithFormat:@"%@", @"横向右OrientationLandscapeRight"];
			break;

		default:
			break;
	}
/*
	UIAlertView* alert = [[UIAlertView alloc]
								  initWithTitle:@"Orientation"
								  message:msg
								  delegate:self
								  cancelButtonTitle:@"OK"
								  otherButtonTitles:nil];
	[alert show];
	[alert release];
*/
	switch (interfaceOrientation) {
		case UIInterfaceOrientationPortrait:
		case UIInterfaceOrientationPortraitUpsideDown:
			self.view = _self_view;
			_button.frame = CGRectMake(20, 170, 280, 37);
			_slider.frame = CGRectMake(18, 178, 284, 23);
			_image.frame = CGRectMake(12, 233, 288, 150);
			words.frame = CGRectMake(25, 256, 208, 21);
			break;
		case UIInterfaceOrientationLandscapeLeft:
			self.view = _landscape_left;
			break;
		case UIInterfaceOrientationLandscapeRight:
			self.view = _self_view;
			_button.frame = CGRectMake(310, 113, 140, 44);
			_slider.frame = CGRectMake(310, 113, 140, 44);
			_image.frame = CGRectMake(10, 153, 450, 100);
			words.frame = CGRectMake(23, 163, 326, 21);
			break;
		default:
			break;
	}
	return YES;
	
}


- (void)didReceiveMemoryWarning {
	// Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
	
	// Release any cached data, images, etc that aren't in use.
}

- (void)viewDidUnload {
	// Release any retained subviews of the main view.
	// e.g. self.myOutlet = nil;
	self.words = nil;
	self.name = nil;
	self.idx = nil;
	self._slider = nil;
	self._button = nil;
	self._self_view = nil;
	self._landscape_left = nil;
	self._landscape_left_words = nil;
}


- (void)dealloc {
	[words release];
	[name release];
	[idx release];
	[_slider release];
	[_button release];
	[_landscape_left_words release];
	[_landscape_left release];
	[_self_view release];
    [super dealloc];
}

@end
