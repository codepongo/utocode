//
//  s.swift
//  objc-swift
//
//  Created by jack on 16/3/31.
//  Copyright © 2016年 zuohaitao. All rights reserved.
//

import Foundation


@objc class S : NSObject{
    let o:O = O()
    func m() {
        o.m()
        print(__FUNCTION__)
    }
}
