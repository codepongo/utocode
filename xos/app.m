/*
 * gcc -ggdb -framework cocoa -x objective-c -o a.app app.m
 */ 
#import <cocoa/cocoa.h>
@interface AppController:NSObject<NSApplicationDelegate,NSWindowDelegate> {
}
@property (nonatomic, retain) IBOutlet NSButton* button;
@property (nonatomic, retain) IBOutlet NSTextField* textfield;
@property (nonatomic, retain) IBOutlet NSSlider* slider;

@end

@implementation AppController
@synthesize button;
@synthesize slider;
@synthesize textfield;

- (void) applicationDidBecomeActive:(NSNotification* )anotification {
	NSLog(@"%s", __FUNCTION__);
}
- (void)applicationWillFinishLaunching:(NSNotification *)aNotification
{
	NSLog(@"%s", __FUNCTION__);
	NSWindow* win = [NSApp mainWindow];
	NSRect wf0 = {{200, 200}, {600, 400}};
	wf0.origin.x = 200;
	wf0.origin.y = 200;
	wf0.size.width = 800;
	wf0.size.height = 600;
	int style = NSTitledWindowMask | NSClosableWindowMask 
		| NSMiniaturizableWindowMask;
	win = [[NSWindow alloc] initWithContentRect: wf0
			  styleMask: style
			  backing: NSBackingStoreBuffered
			  defer: NO];
	[win setDelegate:self];
	NSRect frame = NSMakeRect(0, 550, 100, 50);
	NSView* view = [[NSView alloc]initWithFrame:[win frame]];

	NSButton* btn = [[NSButton alloc]initWithFrame:frame];
	button = btn;
	//btn.bezelStyle = NSRoundedBezelStyle;
	[win setContentView:view];
	[[win contentView] addSubview:btn];
	btn.target = self;
	btn.action = @selector(clicked:);
	[btn performClick:self];
	[btn autorelease];


	NSSlider* s = [[NSSlider alloc] initWithFrame:NSMakeRect(100, 580, 100, 20)];
	slider = s;
	[slider setAutoresizingMask: (NSViewWidthSizable)];
  [slider setTitle: @"Slider Title"];
	[slider setMinValue: 0];
	[slider setMaxValue: 100];
	[slider setFloatValue: 1];
	slider.target = self;
	slider.action = @selector(sliderChanged:);
	[[win contentView] addSubview:slider];
	[slider autorelease];

	NSTextField* input = [[NSTextField alloc] initWithFrame:NSMakeRect(200, 580, 100, 20)];
	textfield = input;
	BOOL b = [textfield isEditable];
	//NSLog(@"%@", [textfield isEditable]);
	//input.target = self;
	//input.action = @selector(inputChanged:);
	[[win contentView] addSubview:input];

	/*
	frame = NSMakeRect(0, 200, 120, 40);
	NSPopUpButton* popUpButton = [[NSPopUpButton alloc] initWithFrame:frame];
	[popUpButton setPullsDown:YES];
	[popUpButton setAutoresizingMask: NSViewMaxXMargin];
	[popUpButton addItemWithTitle: @"PNG"];
	[popUpButton addItemWithTitle: @"JPEG"];
	[popUpButton addItemWithTitle: @"PDF"];
	[popUpButton addItemWithTitle: @"TIFF"];
	popUpButton.target = self;
	popUpButton.action = @selector(clicked:);
	[[win contentView] addSubview:popUpButton];
	NSLog(@"popUpButton itemArray: %@", popUpButton.itemArray);
	NSLog(@"popUpButton itemTitles: %@", popUpButton.itemTitles);
	[popUpButton removeItemWithTitle: @"JPEG"];
	NSLog(@"popUpButton itemTitles: %@", popUpButton.itemTitles);
	[[popUpButton itemWithTitle: @"TIFF"] setTitle:@"M4V"];
	NSLog(@"popUpButton itemTitles: %@", popUpButton.itemTitles);
	//[popUpButton removeAllItems];
	NSLog(@"popUpButton itemTitles: %@", popUpButton.itemTitles);
	[popUpButton setEnable:YES];
	[popUpButton autorelease];
	*/
	[view release];
	/*
	_view = [ [ ZGlView alloc ] initWithFrame:[ win frame ]
										  colorBits:16 depthBits:16 fullscreen:FALSE ];
 
	[win setContentView:_view];
*/
	[win orderFrontRegardless];
  [win becomeKeyWindow];

  NSLog(@"%d", [NSApp activationPolicy]);
}

- (IBAction) clicked:(id)sender {
	NSLog(@"%s:%@", __FUNCTION__, sender);
	NSWindow* win = [NSApp mainWindow];
	NSLog(@"%x", [win isKeyWindow]);
	NSLog(@"0x%x", [NSApp keyWindow]);
	NSLog(@"0x%x", win);
}

- (IBAction) sliderChanged:(id)sender {
	NSLog(@"%s:%@", __FUNCTION__, sender);
	NSLog(@"%d", [sender intValue]);
}

- (IBAction) inputChanged:(id)sender {
	NSLog(@"%s:%@", __FUNCTION__, sender);
	NSLog(@"%@", [sender stringValue]);
}
/*
- (IBAction) popuped:(id)sender {
	NSLog(@"%s:%@", __FUNCTION__, sender);
}
*/
@end


int
main(int argc, char** argv)
{
	id pool = [[NSAutoreleasePool alloc]init];
	[NSApplication sharedApplication];
	[NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
	id appcontroller = [[AppController alloc]init];
	[NSApp setDelegate:appcontroller];
	[NSApp run];
	[pool release];
	return 0;
}
