//
//  rootViewController.h
//  say
//
//  Created by zuohaitao on 12-1-9.
//  Copyright 2012 zuohaitao@doaob. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "birthdayViewController.h"
#import "noteViewController.h"
#import "sayViewController.h"

@class birthdayViewController;
@class noteViewController;

@interface rootViewController : UIViewController {
	birthdayViewController* birthday;
	noteViewController* note;
	sayViewController* say;

}
@property (retain, nonatomic) birthdayViewController *birthday;
@property (retain, nonatomic) noteViewController *note;
@property (retain, nonatomic) sayViewController *say;

- (IBAction)switchViews:(id)sender;

@end
