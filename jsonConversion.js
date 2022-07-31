// this file is for updating schema in the eventLibrary (when it was stored as json)
// make sure to run node jsonConversion.js from cli

const uuid = require("uuid");
const parsedLibrary = require("./eventLibrary.json");

const stringToSlug = (str) => {
  // credit to https://gist.github.com/codeguy/6684588
  let newStr = str;
  newStr = newStr.replace(/^\s+|\s+$/g, ""); // trim
  newStr = newStr.toLowerCase();

  // remove accents, swap ñ for n, etc
  const from = "àáäâèéëêìíïîòóöôōùúüûñç·/_,:;";
  const to = "aaaaeeeeiiiiooooouuuunc------";
  for (let i = 0, l = from.length; i < l; i++) {
    newStr = newStr.replace(new RegExp(from.charAt(i), "g"), to.charAt(i));
  }

  newStr = newStr
    .replace(/[^a-z0-9 -]/g, "") // remove invalid chars
    .replace(/\s+/g, "-") // collapse whitespace and replace by -
    .replace(/-+/g, "-"); // collapse dashes

  return newStr;
};

// conversion
const formatDate = (dateString) => {
  const dateNoSuffix = dateString.replace(/(\d+)(st|nd|rd|th)/, "$1");
  const rawDateObj = new Date(dateNoSuffix);
  // MM/DD/YYYY
  return `${
    rawDateObj.getMonth() + 1
  }/${rawDateObj.getDate()}/${rawDateObj.getFullYear()}`;
};

const newLibrary = [];
Object.keys(parsedLibrary).forEach((dayString) => {
  const dayEvents = parsedLibrary[dayString];
  dayEvents.forEach((dayEvent) => {
    newLibrary.push({
      id: uuid.v4(),
      title: dayEvent.title,
      slugTitle: stringToSlug(dayEvent.title),
      otd: dayEvent.otd,
      description: dayEvent.description,
      category: dayEvent.category,
      imgAltText: dayEvent.imgAltText,
      NSFW: dayEvent.NSFW,
      imgSrc: dayEvent.imgSrc.replace("/assets/eventPhotos/", ""),
      date: formatDate(dayEvent.date),
      sources: [dayEvent.infoSrc, dayEvent.link],
    });
  });
});

const fs = require("fs");

const newEventLibrary = JSON.stringify(newLibrary);

fs.writeFile("newEventLibrary.json", newEventLibrary, function (err) {
  if (err) console.log(err);
  else console.log("Write operation complete.");
});
