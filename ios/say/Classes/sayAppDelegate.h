//
//  sayAppDelegate.h
//  say
//
//  Created by zuohaitao on 11-12-10.
//  Copyright 2011 zuohaitao@doaob. All rights reserved.
//

#import <UIKit/UIKit.h>

@class rootViewController;
@interface sayAppDelegate : NSObject <UIApplicationDelegate> {
    UIWindow *window;
	rootViewController *viewController;
}

@property (nonatomic, retain) IBOutlet UIWindow *window;
@property (nonatomic, retain) IBOutlet rootViewController *viewController;

@end

