//
//  sayAppDelegate.m
//  say
//
//  Created by zuohaitao on 11-12-10.
//  Copyright 2011 zuohaitao@doaob. All rights reserved.
//

#import "sayAppDelegate.h"
#import "rootViewController.h"

@implementation sayAppDelegate

@synthesize window;
@synthesize viewController;


#pragma mark -
#pragma mark Application lifecycle

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {    
    NSLog(@"%s", __FUNCTION__);
    // Override point for customization after application launch.

	// Set the view controller as the window's root view controller and display.
	[self.window addSubview:self.viewController.view]; 
	
    [self.window makeKeyAndVisible];

    return YES;
}


- (void)applicationWillResignActive:(UIApplication *)application {
    /*
     Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
     Use this method to pause ongoing tasks, disable timers, and throttle down OpenGL ES frame rates. Games should use this method to pause the game.
     */
}


- (void)applicationDidEnterBackground:(UIApplication *)application {
    /*
     Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later. 
     If your application supports background execution, called instead of applicationWillTerminate: when the user quits.
     */
	NSLog(@"%s", __FUNCTION__);
	UILocalNotification *notification=[[UILocalNotification alloc] init]; 
	if (notification!=nil) { 
		NSLog(@">> support local notification"); 
		NSDate *now=[NSDate new]; 
		notification.fireDate=[now dateByAddingTimeInterval:10/*60*60*/];
		notification.timeZone=[NSTimeZone defaultTimeZone]; 
		notification.alertBody=@"小胖子，我爱你";
		notification.alertAction = @"老公";
		notification.applicationIconBadgeNumber = 100;
		notification.soundName = @"ping.caf";
		[[UIApplication sharedApplication]   scheduleLocalNotification:notification];
	}
}

- (void)didReceiveLocalNotification:(UILocalNotification *)notification {
	NSLog(@"%s", __FUNCTION__);
	notification.applicationIconBadgeNumber = notification.applicationIconBadgeNumber-1;
}

- (void)applicationWillEnterForeground:(UIApplication *)application {
    /*
     Called as part of  transition from the background to the inactive state: here you can undo many of the changes made on entering the background.
     */
}


- (void)applicationDidBecomeActive:(UIApplication *)application {
    /*
     Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
     */
}


- (void)applicationWillTerminate:(UIApplication *)application {
    /*
     Called when the application is about to terminate.
     See also applicationDidEnterBackground:.
     */
	NSLog(@"%s", __FUNCTION__);
	
}


#pragma mark -
#pragma mark Memory management

- (void)applicationDidReceiveMemoryWarning:(UIApplication *)application {
    /*
     Free up as much memory as possible by purging cached data objects that can be recreated (or reloaded from disk) later.
     */
}


- (void)dealloc {
    [viewController release];
    [window release];
    [super dealloc];
}


@end
