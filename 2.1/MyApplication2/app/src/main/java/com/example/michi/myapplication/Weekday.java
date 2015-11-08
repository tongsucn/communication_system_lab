package com.example.michi.myapplication;

import java.util.ArrayList;
import java.util.List;
import java.lang.String;

/**
 * Created by michi on 02.11.2015.
 * Property class to represent the available food for a specific weekday.
 */
class Weekday {
    private String day; // e.g. "montag" (in german).
    private String date; // e.g. "Monday November 02, 2015".
    private final List<Dish> dishes; // e.g. "No data available for this period!".
    private String note;

    public Weekday() {
        this.day = "";
        this.date = "";
        this.note = "";
        this.dishes = new ArrayList<>();
    }

    public void setDay(String day) {
        this.day = day;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public void addDish(Dish dish) {
        this.dishes.add(dish);
    }

    public String getDay() {
        return this.day;
    }

    public String getDate() {
        return this.date;
    }

    public List<Dish> getDishes() {
        return this.dishes;
    }



    public String getNote() {
        return this.note;
    }
}
