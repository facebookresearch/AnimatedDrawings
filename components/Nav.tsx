import { Disclosure } from "@headlessui/react";
import Link from "next/link";
import Image from "next/image";
import { assetLoader } from "../lib/paths";
import { RiArrowRightUpLine } from "react-icons/ri";

import { RiMenuFill, RiCloseCircleFill } from "react-icons/ri";

const Site = require("../site.json");

export default function Nav({ items, selected }) {
  const color = Site.theme;

  const logoWithLink = (logo) => {
    return Site.showHomeLink ? (
      <div className="flex-shrink-0 flex items-center cursor-pointer">
        {logo}
      </div>
    ) : (
      <Link href={`/home`} passHref>
        <div className="flex-shrink-0 flex items-center cursor-pointer">
          {logo}
        </div>
      </Link>
    );
  };

  return (
    <Disclosure as="nav" className="bg-white md:shadow">
      {({ open }) => (
        <>
          <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                {logoWithLink(
                  <Image
                    src={Site.logo}
                    alt="logo"
                    height={32}
                    width={32}
                    loader={assetLoader}
                  />
                )}

                {/* Web menu */}
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {items &&
                    items.map((item) =>
                      Site.showHomeLink || item.id !== "home" ? (
                        <Link href={`/${item.id}`} key={item.id} passHref>
                          <a
                            className={`${
                              selected === item.id ? `text-${color}-700` : ""
                            } hover:text-${color}-500 text-gray-900 inline-flex items-center px-1 pt-1 text-sm font-semibold`}
                          >
                            {item.title}
                          </a>
                        </Link>
                      ) : null
                    )}
                </div>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {Site.rightNav &&
                  Site.rightNav.map((item) => (
                    <a
                      href={item.url}
                      key={item.title}
                      className={`text-gray-900 hover:text-${color}-500 ml-6 inline-flex items-center px-1 pt-1 text-sm font-semibold`}
                      target="_blank"
                    >
                      {item.title}&nbsp;
                      <RiArrowRightUpLine />
                    </a>
                  ))}
              </div>
              <div className="-mr-2 flex items-center sm:hidden">
                {/* Mobile menu button */}
                <Disclosure.Button
                  className={`inline-flex items-center justify-center p-2 rounded-md text-gray-900`}
                >
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <RiCloseCircleFill
                      className="block h-6 w-6"
                      aria-hidden="true"
                    />
                  ) : (
                    <RiMenuFill className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
            </div>
          </div>

          {/* Mobile Menu */}
          <Disclosure.Panel className="sm:hidden">
            {({ close }) => (
              <div className="pt-2 pb-3 space-y-1 absolute left-0 right-0 z-50 bg-white shadow-xl">
                {items &&
                  items.map((item) =>
                    Site.showHomeLink || item.id !== "home" ? (
                      <Link
                        href={`/${item.id}`}
                        key={item.id}
                        passHref
                        prefetch
                      >
                        <Disclosure.Button
                          as="a"
                          onClick={async () => setTimeout(close, 500)}
                          className={`${
                            selected === item.id
                              ? `bg-${color}-50 text-${color}-700`
                              : "text-gray-900"
                          } block pl-5 pr-4 py-2 text-base font-semibold`}
                        >
                          {item.title}
                        </Disclosure.Button>
                      </Link>
                    ) : null
                  )}

                {Site.rightNav &&
                  Site.rightNav.map((item) => (
                    <Disclosure.Button
                      as="a"
                      href={item.url}
                      key={item.title}
                      className="text-gray-900 block pl-5 pr-4 py-2 border-none text-base font-semibold"
                    >
                      {item.title}<span className="inline-block align-middle"><RiArrowRightUpLine /></span>
                    </Disclosure.Button>
                  ))}
              </div>
            )}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
