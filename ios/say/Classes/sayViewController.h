//
//  sayViewController.h
//  say
//
//  Created by zuohaitao on 11-12-10.
//  Copyright 2011 zuohaitao@doaob. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface sayViewController : UIViewController<UIActionSheetDelegate> {
	UILabel* words;
	UITextField* name;
	UITextField* idx;
	UIButton* _button;
	UISlider* _slider;
	UIImageView* _image;
	UIView* _self_view;
	UIView* _landscape_left;
	UILabel* _landscape_left_words;
}

@property (nonatomic, retain) IBOutlet UILabel* words;
@property (nonatomic, retain) IBOutlet UITextField* name;
@property (nonatomic, retain) IBOutlet UITextField* idx;
@property (nonatomic, retain) IBOutlet UIButton* _button;
@property (nonatomic, retain) IBOutlet UISlider* _slider;
@property (nonatomic, retain) IBOutlet UIImageView* _image;
@property (nonatomic, retain) IBOutlet UIView* _self_view;
@property (nonatomic, retain) IBOutlet UIView* _landscape_left;
@property (nonatomic, retain) IBOutlet UIView* _landscape_left_words;


-(IBAction)say:(id)sender;
-(IBAction)textFieldDoneEditing:(id)sender;
-(IBAction)backgroundTap:(id)sender;
-(IBAction)sliderChanged:(id)sender;
-(IBAction)segmentChanged:(id)sender;
-(IBAction)switchChanged:(id)sender;

@end

