package com.journaldev.loginphpmysql.ui.main;

import android.content.Context;
import android.support.annotation.Nullable;
import android.support.annotation.StringRes;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;

import com.journaldev.loginphpmysql.Profile;
import com.journaldev.loginphpmysql.Search;
import com.journaldev.loginphpmysql.Posts;
import com.journaldev.loginphpmysql.R;

/**
 * A [FragmentPagerAdapter] that returns a fragment corresponding to
 * one of the sections/tabs/pages.
 */
public class SectionsPagerAdapter extends FragmentPagerAdapter {

    private final Context mContext;



    public SectionsPagerAdapter(Context context, FragmentManager fm) {
        super(fm);
        mContext = context;
    }

    @Override
    public Fragment getItem(int position) {
        Fragment fragment =null;
        switch (position){
            case 0:
                fragment = new Profile();
                break;
            case 1:
                fragment = new Search();
                break;
            case 2:
                fragment = new Posts();
                break;
        }
        return fragment;
    }


    @Override
    public int getCount() {
        // Show 3 total pages.
        return 3;
    }
}